# pipeline.py
import os, time, math, json, unicodedata
from pathlib import Path
from typing import List, Dict

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
import gspread
from tqdm import tqdm
import re
import math
from pathlib import Path

# ---------- 0. 환경 로드 ----------
YOUTUBE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---------- 1. YouTube 검색 ----------

YOUTUBE = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)  
# ---------- 스코어 계산 함수 ----------
# 예시: (조회수 * 0.7 + 좋아요 * 50 * 0.3) 의 로그 스케일
def calc_score(views: int, likes: int) -> float:
    raw = 0.7 * views + 0.3 * 50 * likes
    return round(math.log10(raw + 1), 3)

# ---------- ISO 8601 → 초 변환 함수 ----------
import isodate

def iso_duration_to_sec(iso_dur: str) -> int:
    try:
        duration = isodate.parse_duration(iso_dur)
        return int(duration.total_seconds())
    except:
        return 0
    
def seconds_to_mmss(seconds):
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes}:{sec:02d}"

def safe_filename(name: str, allow_unicode: bool = True, max_len: int = 80) -> str:
    # 유니코드 NFC 정규화 → 윈도우 한글 결합형 문제 방지
    name = unicodedata.normalize("NFC", name) if allow_unicode else unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[\\/*?:\"<>|]", "", name)      # 금지 문자 삭제
    name = re.sub(r"\s+", " ", name).strip()       # 공백 정리
    return name[:max_len]

def _snippet_text(snippet) -> str:
    """
    • 0.6.x → snippet is dict  → snippet["text"]
    • 1.x   → snippet is FetchedTranscriptSnippet → snippet.text
    """
    if isinstance(snippet, dict):
        return snippet.get("text", "")
    return getattr(snippet, "text", "")

# ---------- 자막(txt) 저장 ----------
def save_transcript(video_id: str, title: str, pref_lang: str, dirname: str | None = None) -> str | None:
    """
    • 자막이 있으면 .txt 저장 후 경로 반환
    • 없으면 None 반환
    """

    
    try:
        # ① 우선 사용자가 지정한 언어로 시도
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[pref_lang])
    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript):
        try:
            # ② 실패하면 "자동 생성(en)" → "자동 생성(ko)" 순으로 fallback
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = (
                transcript_list.find_generated_transcript(['en', 'ko']).fetch()
            )
        except Exception:
            return "save_transcript 실패"
            #return None  # 완전히 실패 → 상위 로직에서 None 체크
    
    # transcript는 list[dict] (0.6.x) 또는 FetchedTranscript (iterable, 1.x)
    text_lines = [_snippet_text(s) for s in transcript]
    transcript_text = "\n".join(text_lines)

    # import unicodedata
    # import tempfile
    
    # def safe_name(name):
    #     name = unicodedata.normalize("NFC", name)
    #     name = re.sub(r"[\\/*?:\"<>|]", "", name)  # Windows 금지문자 제거
    #     return name.strip()[:80]
    
    # filename = f"{safe_name(title)}.txt"
    
    # # 로컬 환경인지 스트림릿 환경인지 확인하여 저장 디렉토리 결정
    # if is_local_environment():  # 이 함수는 아래에 정의
    #     # 로컬 환경일 때는 원래 경로에 저장
    #     base_dir = Path.home() / "Downloads"  # C:\Users\<id>\Downloads (Win) 또는 /Users/<id>/Downloads (mac)
    #     save_dir = base_dir / (dirname or "transcripts")
    #     save_dir.mkdir(parents=True, exist_ok=True)
    # else:
    #     # 스트림릿 환경일 때는 임시 디렉토리에 저장
    #     if dirname:
    #         save_dir = Path(tempfile.gettempdir()) / dirname
    #         save_dir.mkdir(parents=True, exist_ok=True)
    #     else:
    #         save_dir = Path(tempfile.gettempdir())
    
    # path = os.path.join(save_dir, filename)
    # with open(path, "w", encoding="utf-8") as f:
    #     f.write(transcript_text)
   
    #return path   
    return transcript_text


# 로컬 환경인지 확인하는 함수
def is_local_environment():
    try:
        # 스트림릿 클라우드는 특정 환경 변수가 설정되어 있음
        return not (os.environ.get('STREAMLIT_SHARING') == 'true' or 
                   'STREAMLIT_SERVER_URL' in os.environ)
    except:
        return True  # 환경 변수 확인 실패 시 안전하게 로컬로 간주
    
# ---------- 메인 파이프라인 ----------
def top3_videos(
    keyword: str,
    start_date: str,  # "YYYY-MM-DD"
    end_date: str,    # "YYYY-MM-DD"
    lang: str = "ko"  # "ko" | "en"
):
    # 1) 검색: 최대 50개 영상 ID 수집 (관련도 순)
    search_resp = YOUTUBE.search().list(
        part="id",
        q=keyword,
        type="video",
        maxResults=50,
        publishedAfter=f"{start_date}T00:00:00Z",
        publishedBefore=f"{end_date}T23:59:59Z",
        relevanceLanguage=lang,
        videoCaption="closedCaption",
        order="relevance",
    ).execute()
    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
    if not video_ids:
        raise ValueError("조건에 맞는 영상이 없습니다.")

    # 2) 상세 정보 조회
    vids_resp = YOUTUBE.videos().list(
        part="snippet,statistics,contentDetails",
        id=','.join(video_ids)
    ).execute()

    # 3) 영상 필터링 및 점수 계산
    videos = []
    for v in vids_resp.get("items", []):
        cd = v["contentDetails"]
        duration = iso_duration_to_sec(cd["duration"])
        # 영상 길이 5분(300초) 이상 필터
        if duration < 300:
            continue

        stats = v.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        score = calc_score(views, likes)
        snippet = v.get("snippet", {})

        videos.append({
            "id": v["id"],
            "title": snippet.get("title", ""),
            "url": f"https://youtu.be/{v['id']}",
            "views": views,
            "upload_date": snippet.get("publishedAt", "")[:10],
            "duration_sec": duration,
            "score": score,
        })

    if len(videos) < 3:
        raise ValueError(f"5분 이상 영상이 {len(videos)}개로 3개 미만입니다.")

    # 4) 점수 기준 상위 3개 선정
    videos.sort(key=lambda x: x["score"], reverse=True)
    top3 = videos[:3]

    return top3
# ---------- 사용 예시 ----------
if __name__ == "__main__":
    
    
    keyword = "미드저니"
    start = "2024-12-01"
    end = "2025-04-29"
    lang = "ko"          # "ko" 이면 한국어 자막 우선

    results = top3_videos(keyword, start, end, lang)
    for idx, r in enumerate(results, 1):
        dur_min = r["duration_sec"] // 60
        print(f"\n[{idx}] {r['title']}")
        print(f"    URL          : {r['url']}")
        print(f"    Views        : {r['views']:,}")
        print(f"    Uploaded     : {r['upload_date']}")
        print(f"    Duration     : {dur_min}분 {r['duration_sec']%60}초")
    
    t_path = save_transcript(results[2]["id"], results[2]["title"], lang)
    print(f"    Transcript    : {t_path}") if t_path else print("    Transcript    : None")

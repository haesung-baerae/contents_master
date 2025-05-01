# pipeline.py
import os, time, math, json, unicodedata
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
import gspread
from tqdm import tqdm
import re
import math
from pathlib import Path
import isodate  # 추가된 import 구문
# ---------- 0. 환경 로드 ----------
YOUTUBE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---------- 1. YouTube 검색 ----------

YOUTUBE = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)  
# ---------- 스코어 계산 함수 ----------
def calc_benchmark_score(video, keyword):
    """
    video: {
        'title': str,
        'description': str,
        'tags': List[str],
        'views': int,
        'likes': int,
        'duration_sec': int,
        'upload_date': datetime
    }
    keyword: str (검색 키워드)
    """

    # 1. 영상 길이 필터링 (3분 미만이면 제외)
    duration_min = video['duration_sec'] / 60
    if duration_min < 3:
        return None  # 점수 계산하지 않음

    # 2. 조회수 점수 (최대 50점, 로그 스케일)
    view_score = math.log10(video['views'] + 1) * 10
    view_score = min(view_score, 50)

    # 3. 좋아요 비율 점수 (likes/views 비율, 최대 20점)
    like_ratio = (video['likes'] / video['views']) if video['views'] else 0
    like_score = min(like_ratio * 100, 20)

    # 4. 영상 길이 점수 (3~30분이면 점수 부여, 최적 범위는 5~20분)
    if 5 <= duration_min <= 20:
        length_score = 20
    elif 3 <= duration_min <= 30:
        length_score = 10
    else:
        length_score = 0

    # 5. 최신성 점수 (30일 이내 = 5점, 90일 이내 = 2점)
    days_ago = (datetime.now() - video['upload_date']).days
    if days_ago <= 30:
        freshness_score = 5
    elif days_ago <= 90:
        freshness_score = 2
    else:
        freshness_score = 0

    # 6. 키워드 포함 점수 (제목, 설명, 태그 기반)
    keyword_lower = keyword.lower()
    title_score = 10 if keyword_lower in video['title'].lower() else 0
    description_score = 5 if keyword_lower in video['description'].lower() else 0
    tags_score = sum(2 for tag in video['tags'] if keyword_lower in tag.lower())
    keyword_score = title_score + description_score + tags_score
    keyword_score = min(keyword_score, 40)  # 최대 40점 제한

    # ✅ 종합 점수 계산 (100점 만점)
    total_score = view_score + like_score + length_score + freshness_score + keyword_score
    return round(total_score, 2)

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
            # ② 실패하면 사용 가능한 언어 목록에서 대체 언어 선택
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = (
                transcript_list.find_transcript(['ko', 'en']).fetch()
            )
        except Exception as e:
            print(f"Failed to fetch transcript for video {video_id}: {e}")
            return None  # 완전히 실패 → 상위 로직에서 None 체크
        
    # 자막이 비어 있는 경우 처리
    if not transcript:
        print(f"No transcript available for video {video_id}")
        return None
        
    # transcript는 list[dict] (0.6.x) 또는 FetchedTranscript (iterable, 1.x)
    text_lines = [_snippet_text(s) for s in transcript]
    transcript_text = "\n".join(text_lines)

 
    return transcript_text
    
    
# ---------- 메인 파이프라인 ----------
def top3_videos(
    keyword: str,
    start_date: str,  # "YYYY-MM-DD"
    end_date: str,    # "YYYY-MM-DD"
    lang: str = "ko"  # "ko" | "en"
):
    # 1) 검색: 최대 50개 영상 ID 수집 (관련도 순)
    search_resp = YOUTUBE.search().list(
        part="id,snippet",
        q=f'"{keyword}"',  # 정확한 구문 검색
        type="video",
        maxResults=50,
        publishedAfter=f"{start_date}T00:00:00Z",
        publishedBefore=f"{end_date}T23:59:59Z",
        relevanceLanguage=lang,
        videoCaption="any",  # 자막 유무 상관없이 검색
        order="relevance",  # 관련도 순으로 정렬
    ).execute()
    video_items = search_resp.get("items", [])
    if not video_items:
        raise ValueError("조건에 맞는 영상이 없습니다.")

    # 2) 상세 정보 조회
    video_ids = [item["id"]["videoId"] for item in video_items]
    vids_resp = YOUTUBE.videos().list(
        part="snippet,statistics,contentDetails",
        id=','.join(video_ids)
    ).execute()

    # 3) 영상 필터링 및 점수 계산
    videos = []
    for v in vids_resp.get("items", []):
		snippet = v.get("snippet", {})
        cd = v["contentDetails"]
		# 언어 필터링 완화: 언어 정보가 없거나 일치하지 않아도 포함
        audio_lang = snippet.get("defaultAudioLanguage", "")
        if lang not in audio_lang and audio_lang:  # 언어 정보가 없으면 포함
            continue

        # 영상 길이 필터링 완화 (30초 이상)
        duration = iso_duration_to_sec(cd["duration"])
        if duration < 30:  # 30초 이상으로 완화
            continue

        stats = v.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        upload_date = datetime.strptime(snippet.get("publishedAt", "")[:10], "%Y-%m-%d")

        # 점수 계산
        video_data = {
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "tags": snippet.get("tags", []),
            "views": views,
            "likes": likes,
            "duration_sec": duration,
            "upload_date": upload_date,
        }
        score = calc_benchmark_score(video_data, keyword)
        if score is None:
            continue
        
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
        print(f"조건에 맞는 영상이 {len(videos)}개로 3개 미만입니다.")
        return videos  # 3개 미만이어도 반환

    # 4) 점수 기준 상위 3개 선정
    videos.sort(key=lambda x: x["score"], reverse=True)
    top3 = videos[:3]

    return top3

# ---------- 사용 예시 ----------
if __name__ == "__main__":
    YOUTUBE = build("youtube", "v3", developerKey=g_api_key)  
    
    keyword = "세계여행"
    start = "2024-10-01"
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
        
        # 모든 추천 영상에 대해 자막 저장 시도
        t_path = save_transcript(r["id"], r["title"], lang)
        print(f"    Transcript    : {t_path}") if t_path else print("    Transcript    : None")

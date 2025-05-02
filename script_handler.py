import streamlit as st
import os
import argparse
from pathlib import Path
from textwrap import dedent

from openai import OpenAI

# 0) 환경 변수(.env) 로드
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)

# 2) 단일 프롬프트 요약 (긴 파일이면 chunking 전략 추가 가능)
def summarize(
    sel_script: str, 
    sentences: int = 3,
    tone: str = "formal",
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
) -> str:    
    """
    text      : 원본 스크립트
    sentences : 몇 문장으로 요약할지(또는 'paragraphs', 'words' 등으로 바꿔도 됨)
    tone      : 'friendly', 'professional', '유머러스한', '논문 스타일' 등 자유 입력
    """
    system_msg = dedent(
        f"""
        You are an expert content summarizer.
        Always base your summary *only* on the given transcript; do not add facts.
        """
    )
    user_msg = dedent(
        f"""
        아래 스크립트를 {tone} 톤으로, {sentences}문장 분량으로 요약해 주세요.
        ---
        {sel_script}
        """
    )

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )
    return resp.choices[0].message.content.strip()

def expand_summary_to_blog(summary_text: str, target_audience = 'all', tone_style="friendly", goal = 'normal', target_chars=500, keyword="AI 부업"):
    """
    요약문을 바탕으로 블로그 글을 생성합니다.
    - 글 구조: 서론, 본론(소제목 포함), 결론
    - SEO 키워드 전략 포함
    """
    prompt = f"""
    아래 요약문을 바탕으로 {tone} 톤의 블로그 글을 작성하세요.
    • 글 전체 분량은 최소 {target_chars}자, 최대 {target_chars + 500}자 사이로 맞춰주세요.
    • 제목, 첫 문단, 소제목에 '{keyword}'를 포함하세요.
    • 소제목은 3~5개로 나누고, 각 소제목마다 200자 이상 작성해주세요.
    • 구체적인 예시나 비유를 하나씩 포함하고, 마지막에는 독자에게 던질 질문이나 제안을 넣어 글을 마무리하세요.
    • 글 구조는 다음과 같이 작성하세요:
        1. 서론: 독자의 관심을 끌고 문제를 정의하며 키워드를 포함.
        2. 본론: 문제 해결 방법, 구체적인 사례, 데이터 및 통계 활용.
        3. 결론: 제목 및 주요 키워드를 포함해 요약과 행동 유도를 명시.
    • SEO 최적화를 위해 키워드를 본문에 최소 3~6회 자연스럽게 배치하세요.

    요약문:
    "{summary_text}"

    블로그 글:
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 뛰어난 블로그 작가입니다. 문장이 풍성하고 읽는 재미가 나도록 써주세요."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=3000,
    )
    text = response.choices[0].message.content.strip()
    
    # 혹시 여기서도 부족하다면, length 체크 후 자동으로 ‘계속’ 요청
    if len(text) < target_chars:
        cont = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "이전 응답이 길이가 부족했습니다. 이어서 작성해주세요."},
                {"role": "user", "content": text}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        text += "\n" + cont.choices[0].message.content.strip()   
    
    return text



# 3) CLI 진입점 -------------------------------------------------------------
def main():
   
    filename = Path("transcripts")/"[테스트 후기] 미드저니 v7 미쳤는데.txt"

    text = read_script(str(filename))
    tone = '전문적인'
    summary = summarize(text, sentences=3, tone=tone)

    print("\n===== 요약 결과 =====\n")
    print(summary)
    
    print("\n===== 블로그 글 =====\n")
    blog_post = expand_summary_to_blog(summary, tone=tone, target_chars=1300)


if __name__ == "__main__":
    main()


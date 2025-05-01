import os
import argparse
from pathlib import Path
from textwrap import dedent

from openai import OpenAI

# 0) 환경 변수(.env) 로드
client = 

# 1) 스크립트 파일 읽기
def read_script(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    return text.strip()

# 2) 단일 프롬프트 요약 (긴 파일이면 chunking 전략 추가 가능)
def summarize(
    text: str,
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
        {text}
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

def expand_summary_to_blog(summary_text: str, tone="friendly", target_chars=1300):
    prompt = f"""
    아래 요약문을 바탕으로 {tone} 톤의 블로그 글을 작성하세요.
    • 글 전체 분량은 최소 {target_chars}자, 최대 {target_chars + 200}자 사이로 맞춰주세요.
    • 소제목 3~5개를 넣고, 각 소제목마다 200자 이상 작성해주세요.
    • 구체적인 예시나 비유를 하나씩 포함하고, 마지막에는 독자에게 던질 질문이나 제안을 넣어 글을 마무리해주세요.

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
    
    #print(f"블로그 글 길이: {len(text)}자")
    #print(text)
    return text



# 3) CLI 진입점 -------------------------------------------------------------
def main():
    # parser = argparse.ArgumentParser(description="스크립트 요약기")
    # parser.add_argument("--file", required=True, help="요약할 .txt 파일 경로")
    # parser.add_argument("--sentences", type=int, default=3, help="요약 문장 수")
    # parser.add_argument(
    #     "--tone",
    #     type=str,
    #     default="친근한",
    #     help="글 톤/스타일 (예: '격식있는', '유머러스한', '논문 스타일')",
    # )
    # parser.add_argument("--save", action="store_true", help="결과를 _summary.txt로 저장")
    # args = parser.parse_args()
    #text = read_script(args.file)
    #summary = summarize(text, sentences=args.sentences, tone=args.tone)
    
    filename = Path("transcripts")/"[테스트 후기] 미드저니 v7 미쳤는데.txt"
    #text = read_script(args.file)
    text = read_script(str(filename))
    tone = '전문적인'
    summary = summarize(text, sentences=3, tone=tone)

    print("\n===== 요약 결과 =====\n")
    print(summary)
    
    print("\n===== 블로그 글 =====\n")
    blog_post = expand_summary_to_blog(summary, tone=tone, target_chars=1300)


    if True:
        out_path = Path(filename).with_suffix("").as_posix() + "_blog.txt"
        Path(out_path).write_text(blog_post, encoding="utf-8")
        print(f"\nSaved to: {out_path}")
        



if __name__ == "__main__":
    main()


from tiktoken import get_encoding

ENC = get_encoding("cl100k_base")  # or tiktoken.encoding_for_model("gpt-4o-mini")

def chunk_text(text, max_tokens=6000):
    tokens = ENC.encode(text)
    for i in range(0, len(tokens), max_tokens):
        yield ENC.decode(tokens[i : i + max_tokens])

# # ▶ chunk 별 1차 요약 → 요약들을 다시 한번 합쳐 최종 요약
# partial_summaries = [
#     summarize(chunk, sentences=3, tone="neutral") 
#     for chunk in chunk_text(long_text)
# ]
# final_summary = summarize(
#     "\n\n".join(partial_summaries),
#     sentences=desired_sentences,
#     tone=desired_tone
# )

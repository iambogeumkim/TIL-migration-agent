import os
import tools
import langchainhub as hub

from dotenv import load_dotenv

from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from langsmith import Client

load_dotenv()

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

langsmith_client = Client(api_key=LANGSMITH_API_KEY)

# 1. Gemini 모델 설정
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 2. 도구 리스트
all_tools = [
    obj for _, obj in tools.__dict__.items() 
    if isinstance(obj, BaseTool)
]

# 4. 에이전트 생성
agent = create_agent(llm, all_tools)

# 5. 실행
mission = """
1. TIL 레포지토리의 루트 경로를 확인해.
2. 각 마크다운 파일의 내용을 읽어서 Gatsby 블로그 형식(YAML Frontmatter 포함)으로 변환해.
   - Frontmatter에는 title, date, description, category를 포함되어야 해.
   - Frontmatter 형식은 다음과 같아:
     ```yaml
     ---
      title: "YYMMDD TIL: 내용과 관련된 키워드"
      date: "YYYY-MM-DDTHH:MM:SS.000+09:00"
      description: "1 day 1 lesson"
      category: "TIL"
      ---
     ```
   - 내용은 원본 본문을 그대로 유지해.
3. 변환된 파일을 Gatsby 블로그 레포지토리에 저장해.
"""

if __name__ == "__main__":
   agent.invoke({"input": mission})
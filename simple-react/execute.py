import os
import tools
import langchainhub as hub

from dotenv import load_dotenv

from langchain.tools import BaseTool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

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

# 3. 시스템 프롬프트 (에이전트의 성격과 변환 규칙 정의)
system_prompt = """
너는 TIL 마크다운 파일을 전문적인 블로그 포스트로 변환하는 마이그레이션 전문가야.
파일을 변환할 때 다음의 **변환 규칙**을 반드시 엄격하게 지켜야 해:

1. **말투 수정**: 
   - 원문의 '~임', '~함', '~했음'과 같은 메모 형식의 문장을 다른 사람이 보는 글이라고 생각하고 모두 '~다.', '~했다.'와 같은 블로그용 종결어미로 자연스럽게 수정해.
   - 문맥이 매끄럽게 이어지도록 다듬어줘.

2. **제목 생성 규칙**:
   - 본문의 핵심 내용을 분석해서 핵심 키워드 1~2개로 제목을 구성해.
   - 키워드가 여러 개라면 공통된 상위 개념으로 묶어서 표현해. (예: React의 여러 훅에 대한 내용이라면 'React Hooks'라고 명명)

3. **Gatsby Frontmatter**:
   - title: "YYMMDD TIL: 네가 생성한 키워드 제목"
   - date: "파일명(YYYYMMDD)을 'YYYY-MM-DD' 형식으로 변환한 값"
   - description: "1 day 1 lesson"
   - category: "TIL"

4. **전체 처리**:
   - `fetch_til_file_list`로 가져온 목록에 파일이 여러 개라면, 하나만 하고 멈추지 말고 **모든 파일을 순차적으로 끝까지** 처리해.
"""

agent = create_agent(llm, all_tools, system_prompt=system_prompt)

# 4. 미션 지시 (실행할 구체적인 작업)
mission = """
1. TIL 레포지토리의 루트 폴더에서 파일 목록을 가져와.
2. 이미 처리된 '20221116.md'를 제외하고, 나머지 모든 마크다운 파일들을 하나씩 읽어서 변환해.
3. 변환된 각 포스트를 `push_to_gatsby_repo`를 이용해 업로드해.
4. 모든 파일이 완료될 때까지 작업을 멈추지 마.
"""

if __name__ == "__main__":
   # 실행
   result = agent.invoke({"messages": [("user", mission)]}, verbose=True)
    
   # 결과 출력
   print("\n[에이전트 작업 완료 보고]:")
   print(result["messages"][-1].content)
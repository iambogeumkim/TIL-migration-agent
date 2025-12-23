import os

from github import Github
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

g = Github(os.getenv("GITHUB_ACCESS_TOKEN"))

@tool
def fetch_til_file_list(path: str = ""):
    """TIL 레포지토리의 특정 경로에 있는 파일 목록을 가져옵니다.
    
    Args:
        path (str): 파일 목록을 가져올 디렉토리 경로입니다. 기본값은 루트("")입니다.
    """
    repo = g.get_repo(os.getenv("SOURCE_REPO"))
    contents = repo.get_contents(path)
    return [c.path for c in contents if c.type == "file" and c.name.endswith(".md")]

@tool
def read_til_file_content(file_path: str):
    """지정한 경로에 있는 마크다운 파일의 텍스트 본문 내용을 읽어옵니다.
    
    Args:
        file_path (str): 읽어올 파일의 전체 경로입니다.
    """
    repo = g.get_repo(os.getenv("SOURCE_REPO"))
    content = repo.get_contents(file_path)
    return content.decoded_content.decode("utf-8")

@tool
def push_to_gatsby_repo(file_name: str, content: str, target_path: str = "content/blog"):
    """변환된 마크다운 내용을 Gatsby 블로그 레포지토리의 지정된 폴더 구조로 저장합니다.
    
    Args:
        file_name (str): 원본 파일 이름 (예: 20251221.md) 입니다.
        content (str): Gatsby 형식(YAML Frontmatter 포함)으로 변환된 마크다운 전체 내용입니다.
        target_path (str): 블로그 포스트가 저장될 기본 경로입니다. 기본값은 "content/blog"입니다.
    """
    repo = g.get_repo(os.getenv("TARGET_REPO"))
    
    # 확장자 제거 후 날짜 추출
    date_part = file_name.replace(".md", "")
    
    if len(date_part) == 8:
        yymmdd = date_part[2:] # 20251221 -> 251221
    else:
        yymmdd = date_part
        
    # 최종 경로 생성: content/blog/TIL-251221/index.md
    final_path = f"{target_path}/TIL-{yymmdd}/index.md"
    commit_msg = f"Auto-migration: {file_name}"
    
    try:
        # 기존 파일 업데이트
        existing_file = repo.get_contents(final_path)
        repo.update_file(final_path, commit_msg, content, existing_file.sha)
        return f"기존 포스트 업데이트 완료: {final_path}"
    except:
        # 파일 새로 생성
        repo.create_file(final_path, commit_msg, content)
        return f"새 포스트 생성 완료: {final_path}"
import os

from github import Github
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

g = Github(os.getenv("GITHUB_ACCESS_TOKEN"))

@tool
def fetch_til_file_list(path=""):
    """TIL 레포지토리의 특정 경로에 있는 파일 목록 가져오기"""
    repo = g.get_repo(os.getenv("SOURCE_REPO"))
    contents = repo.get_contents(path)
    return [c.path for c in contents if c.type == "file" and c.name.endswith(".md")]

@tool
def read_til_file_content(file_path):
    """지정한 경로의 TIL 파일 내용을 읽어옵니다."""
    repo = g.get_repo(os.getenv("SOURCE_REPO"))
    content = repo.get_contents(file_path)
    return content.decoded_content.decode("utf-8")

@tool
def push_to_gatsby_repo(file_name: str, content: str, target_path: str = "content/blog"):
    """변환된 마크다운 내용을 Gatsby 블로그 레포의 content/blog 폴더에 저장합니다."""
    repo = g.get_repo(os.getenv("TARGET_REPO"))
    
    date_part = file_name.replace(".md", "")
    
    if len(date_part) == 8:
        yymmdd = date_part[2:]
    else:
        yymmdd = date_part
        
    target_path = f"{target_path}/TIL-{yymmdd}/index.md"
    commit_msg = f"Auto-migration: {file_name}"
    
    try:
        # 기존 파일 업데이트
        existing_file = repo.get_contents(target_path)
        repo.update_file(target_path, commit_msg, content, existing_file.sha)
        return f"기존 포스트 업데이트: {target_path}"
    except:
        # 파일 새로 생성
        repo.create_file(target_path, commit_msg, content)
        return f"새 포스트 생성: {target_path}"
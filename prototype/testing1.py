import streamlit as st
import os
import json
import tempfile
from github import Github
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()

# Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")


TEMPLATE_DIR = Path(__file__).parent.parent / "backend" / "templates"
THEMES = {
    "Theme 1": "theme1.html",
    "Theme 2": "theme2.html",
    "Theme 3": "theme3.html",
    "Theme 4": "theme4.html"
    
}

def render_html(resume_json, template_file):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_file)
    return template.render(resume=resume_json)

def create_github_repo(username, html_content, resume_json, selected_theme):
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    repo_name = f"{username.replace(' ', '-').lower()}-portfolio"

    
    repo = user.create_repo(repo_name, private=False, auto_init=True)

    
    repo.create_file("index.html", "Add portfolio page", html_content, branch="main")

    
    resume_bytes = json.dumps(resume_json, indent=2).encode("utf-8")
    repo.create_file("resume.json", "Add resume JSON", resume_bytes.decode(), branch="main")

    
    workflow = f"""name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/configure-pages@v3
    - uses: actions/upload-pages-artifact@v2
      with:
        path: .
    - uses: actions/deploy-pages@v2
"""
    repo.create_file(".github/workflows/deploy.yaml", "Add CI workflow", workflow, branch="main")

   
    enable_github_pages(repo_name)

    return f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"

def enable_github_pages(repo_name):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code not in [201, 204]:
        raise Exception(f" Failed to enable GitHub Pages: {response.status_code} {response.text}")


st.set_page_config(page_title="Portfolio Builder", layout="centered")
st.title("🌐 Resume → Portfolio Website Generator")

resume_file = st.file_uploader("Upload Resume JSON", type=["json"])
selected_theme = st.selectbox("Choose a Theme", list(THEMES.keys()))

if resume_file and st.button("🚀 Generate & Deploy Portfolio"):
    with st.spinner("Processing..."):

        # Load Resume
        resume_json = json.load(resume_file)

        # Render HTML
        html = render_html(resume_json, THEMES[selected_theme])

      
        username = resume_json["name"]
        url = create_github_repo(username, html, resume_json, THEMES[selected_theme])

        st.success(f"Portfolio deployed at: [🔗 {url}]({url})")

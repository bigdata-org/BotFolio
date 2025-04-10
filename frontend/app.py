import streamlit as st
import os
import json
from github import Github
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from dotenv import load_dotenv
import requests
import tempfile
import copy

load_dotenv()

# Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

# template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "backend" / "templates"

# Set up the correct path to your images
PREVIEW_DIR = Path(__file__).parent.parent / "backend" / "static" / "images"
os.makedirs(PREVIEW_DIR, exist_ok=True)


THEMES = {
    "Theme 1": {
        "file": "theme1.html",
        "description": "Modern dark blue theme with teal accents. Professional design with card-based layout."
    },
    "Theme 2": {
        "file": "theme2.html",
        "description": "Vibrant purple/pink gradient design. Creative layout with timeline experience section."
    },
    "Theme 3": {
        "file": "theme3.html",
        "description": "Clean, light theme with teal/amber accents. Minimal and elegant professional style."
    },
    "Theme 4": {
        "file": "theme4.html",
        "description": "Bold slate blue with red accents. Interactive design with modern visual elements."
    }
}

def render_html(resume_json, template_file):
    """Render HTML template with resume data"""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_file)
    return template.render(resume=resume_json)

def create_github_repo(username, html_content, resume_json, template_file):
    """Create and deploy GitHub repository with portfolio"""
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    repo_name = f"{username.replace(' ', '-').lower()}-portfolio"
    
    try:
        
        try:
            repo = user.create_repo(repo_name, private=False, auto_init=True)
        except:
            # Repo might exist, get it instead
            repo = user.get_repo(repo_name)
        
        # Add files
        try:
            contents = repo.get_contents("index.html")
            repo.update_file("index.html", "Update portfolio page", html_content, contents.sha, branch="main")
        except:
            repo.create_file("index.html", "Add portfolio page", html_content, branch="main")
        
        # Add resume JSON
        resume_bytes = json.dumps(resume_json, indent=2).encode("utf-8")
        try:
            contents = repo.get_contents("resume.json")
            repo.update_file("resume.json", "Update resume JSON", resume_bytes.decode(), contents.sha, branch="main")
        except:
            repo.create_file("resume.json", "Add resume JSON", resume_bytes.decode(), branch="main")
        
        # Add GitHub Pages workflow
        workflow = """name: Deploy to GitHub Pages

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
        try:
            contents = repo.get_contents(".github/workflows/deploy.yaml")
            repo.update_file(".github/workflows/deploy.yaml", "Update CI workflow", workflow, contents.sha, branch="main")
        except:
            try:
                repo.create_file(".github/workflows/deploy.yaml", "Add CI workflow", workflow, branch="main")
            except:
                
                pass  # GitHub will create directories automatically when creating files
        
        # Enable GitHub Pages
        enable_github_pages(repo_name)
        
        return f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"
    
    except Exception as e:
        st.error(f"Error creating repository: {str(e)}")
        return None

def enable_github_pages(repo_name):
    """Enable GitHub Pages for the repository"""
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
        st.warning(f"Note: GitHub Pages may take a few minutes to deploy. Status code: {response.status_code}")

def display_theme_selector():
    """Display theme selection cards with static image previews"""
    st.subheader("Choose a Theme")

    cols = st.columns(2)
    
    for i, theme_name in enumerate(THEMES.keys()):
        col = cols[i % 2]
        with col:
            st.markdown(f"### {theme_name}")
            st.markdown(f"*{THEMES[theme_name]['description']}*")

            # Preview image
            image_found = False
            for ext in ['png', 'jpg', 'jpeg']:
                preview_path = PREVIEW_DIR / f"{theme_name.lower().replace(' ', '_')}_preview.{ext}"
                if preview_path.exists():
                    col.image(str(preview_path), caption=f"Preview of {theme_name}", use_container_width=True)
                    image_found = True
                    break
            if not image_found:
                col.image(f"https://via.placeholder.com/600x400?text={theme_name}+Preview",
                          caption=f"Preview of {theme_name}", use_container_width=True)
            
            # Theme selection button
            if col.button(f"Select {theme_name}", key=f"select_button_{theme_name}"):
                st.session_state.selected_theme = theme_name
                st.session_state.theme_selected = True
                st.success(f"✅ You selected **{theme_name}**.")
                return  

def edit_resume_data(resume_data):
    """Interactive editor for resume data with unique keys for all elements"""
    edited_resume = copy.deepcopy(resume_data)
    
    with st.expander("Edit Personal Information", expanded=True):
        # Determine the correct structure based on the JSON
        if "personal_info" in resume_data:
            # Old structure
            personal_info = edited_resume.get("personal_info", {})
            personal_info["name"] = st.text_input("Full Name", personal_info.get("name", ""), key="personal_name")
            personal_info["email"] = st.text_input("Email", personal_info.get("email", ""), key="personal_email")
            personal_info["phone"] = st.text_input("Phone", personal_info.get("phone", ""), key="personal_phone")
            personal_info["location"] = st.text_input("Location", personal_info.get("location", ""), key="personal_location")
            personal_info["linkedin"] = st.text_input("LinkedIn Username", personal_info.get("linkedin", ""), key="personal_linkedin")
            personal_info["github"] = st.text_input("GitHub Username", personal_info.get("github", ""), key="personal_github")
            edited_resume["personal_info"] = personal_info
        else:
            # New structure
            edited_resume["name"] = st.text_input("Full Name", edited_resume.get("name", ""), key="direct_name")
            edited_resume["email"] = st.text_input("Email", edited_resume.get("email", ""), key="direct_email")
            edited_resume["phone"] = st.text_input("Phone", edited_resume.get("phone", ""), key="direct_phone")
            edited_resume["location"] = st.text_input("Location", edited_resume.get("location", ""), key="direct_location")
            edited_resume["LinkedIn"] = st.text_input("LinkedIn URL", edited_resume.get("LinkedIn", ""), key="direct_linkedin")
            edited_resume["GitHub"] = st.text_input("GitHub URL", edited_resume.get("GitHub", ""), key="direct_github")
    
    with st.expander("Edit Education"):
        if "education" in resume_data:
            education_list = edited_resume.get("education", [])
            
            
            updated_education = []
            for i, edu in enumerate(education_list):
                st.markdown(f"### Education #{i+1}")
                
                
                if "institution" in edu:
                    # Old structure
                    edu_item = {
                        "institution": st.text_input(f"Institution #{i+1}", edu.get("institution", ""), key=f"edu_inst_{i}"),
                        "degree": st.text_input(f"Degree #{i+1}", edu.get("degree", ""), key=f"edu_degree_{i}"),
                        "start_date": st.text_input(f"Start Date #{i+1}", edu.get("start_date", ""), key=f"edu_start_{i}"),
                        "end_date": st.text_input(f"End Date #{i+1}", edu.get("end_date", ""), key=f"edu_end_{i}")
                    }
                else:
                    # New structure
                    edu_item = {
                        "university": st.text_input(f"University #{i+1}", edu.get("university", ""), key=f"edu_uni_{i}"),
                        "location": st.text_input(f"Location #{i+1}", edu.get("location", ""), key=f"edu_loc_{i}"),
                        "degree": st.text_input(f"Degree #{i+1}", edu.get("degree", ""), key=f"edu_deg_{i}")
                    }
                    
                    if "expected_graduation" in edu:
                        edu_item["expected_graduation"] = st.text_input(f"Expected Graduation #{i+1}", 
                                                                      edu.get("expected_graduation", ""), key=f"edu_grad_{i}")
                    elif "period" in edu:
                        edu_item["period"] = st.text_input(f"Period #{i+1}", edu.get("period", ""), key=f"edu_period_{i}")
                    
                    if "related_coursework" in edu:
                        coursework_str = ", ".join(edu.get("related_coursework", []))
                        new_coursework = st.text_input(f"Related Coursework #{i+1} (comma-separated)", 
                                                     coursework_str, key=f"edu_courses_{i}")
                        edu_item["related_coursework"] = [course.strip() for course in new_coursework.split(",")] if new_coursework else []
                    
                    if "gpa" in edu:
                        edu_item["gpa"] = st.text_input(f"GPA #{i+1}", edu.get("gpa", ""), key=f"edu_gpa_{i}")
                
                updated_education.append(edu_item)
                st.markdown("---")
            
            edited_resume["education"] = updated_education
    
    with st.expander("Edit Skills"):
        if "skills" in resume_data:
            skills = edited_resume.get("skills", {})
            
            # For each skill category
            updated_skills = {}
            for idx, (category, skill_list) in enumerate(skills.items()):
                st.markdown(f"### {category}")
                
                
                safe_category = f"skills_cat_{idx}"
                skills_str = ", ".join(skill_list)
                new_skills = st.text_input(f"Skills for {category} (comma-separated)", skills_str, key=safe_category)
                updated_skills[category] = [skill.strip() for skill in new_skills.split(",")] if new_skills else []
                
                st.markdown("---")
            
            edited_resume["skills"] = updated_skills
    
    with st.expander("Edit Work Experience"):
        if "work_experience" in resume_data:
            experience_list = edited_resume.get("work_experience", [])
            
            # For each work experience entry
            updated_experience = []
            for i, exp in enumerate(experience_list):
                st.markdown(f"### Work Experience #{i+1}")
                
                # Check which structure we're dealing with
                if "role" in exp:
                    # Old structure
                    exp_item = {
                        "company": st.text_input(f"Company #{i+1}", exp.get("company", ""), key=f"exp_company_{i}"),
                        "role": st.text_input(f"Role #{i+1}", exp.get("role", ""), key=f"exp_role_{i}"),
                        "start_date": st.text_input(f"Start Date #{i+1}", exp.get("start_date", ""), key=f"exp_start_{i}"),
                        "end_date": st.text_input(f"End Date #{i+1}", exp.get("end_date", ""), key=f"exp_end_{i}")
                    }
                else:
                    # New structure
                    exp_item = {
                        "company": st.text_input(f"Company #{i+1}", exp.get("company", ""), key=f"exp_company_{i}"),
                        "title": st.text_input(f"Title #{i+1}", exp.get("title", ""), key=f"exp_title_{i}"),
                        "period": st.text_input(f"Period #{i+1}", exp.get("period", ""), key=f"exp_period_{i}"),
                        "location": st.text_input(f"Location #{i+1}", exp.get("location", ""), key=f"exp_loc_{i}")
                    }
                
                # Handle responsibilities
                if "responsibilities" in exp:
                    resp_list = exp.get("responsibilities", [])
                    updated_resp = []
                    
                    for j, resp in enumerate(resp_list):
                        new_resp = st.text_area(f"Responsibility #{i+1}.{j+1}", resp, key=f"resp_{i}_{j}")
                        updated_resp.append(new_resp)
                    
                    # Option to add a new responsibility
                    if st.button(f"+ Add Responsibility for Job #{i+1}", key=f"add_resp_{i}"):
                        updated_resp.append("")
                    
                    exp_item["responsibilities"] = updated_resp
                
                updated_experience.append(exp_item)
                st.markdown("---")
            
            edited_resume["work_experience"] = updated_experience
    
    with st.expander("Edit Projects"):
        if "projects" in resume_data:
            project_list = edited_resume.get("projects", [])
            
            # For each project entry
            updated_projects = []
            for i, proj in enumerate(project_list):
                st.markdown(f"### Project #{i+1}")
                
                # Check which structure we're dealing with
                if "title" in proj:
                    # Old structure
                    proj_item = {
                        "title": st.text_input(f"Project Title #{i+1}", proj.get("title", ""), key=f"proj_title_{i}"),
                        "description": st.text_area(f"Project Description #{i+1}", proj.get("description", ""), key=f"proj_desc_{i}"),
                        "github_url": st.text_input(f"GitHub URL #{i+1}", proj.get("github_url", ""), key=f"proj_github_{i}")
                    }
                else:
                    # New structure
                    proj_item = {
                        "name": st.text_input(f"Project Name #{i+1}", proj.get("name", ""), key=f"proj_name_{i}"),
                        "description": st.text_area(f"Project Description #{i+1}", proj.get("description", ""), key=f"proj_desc_{i}"),
                        "url": st.text_input(f"Project URL #{i+1}", proj.get("url", ""), key=f"proj_url_{i}")
                    }
                
                # Handle technologies
                if "technologies" in proj:
                    tech_str = ", ".join(proj.get("technologies", []))
                    new_tech = st.text_input(f"Technologies for Project #{i+1} (comma-separated)", 
                                           tech_str, key=f"proj_tech_{i}")
                    proj_item["technologies"] = [tech.strip() for tech in new_tech.split(",")] if new_tech else []
                
                updated_projects.append(proj_item)
                st.markdown("---")
            
            edited_resume["projects"] = updated_projects
    
    # Export JSON button
    if st.button("Save Edited Resume", key="save_resume_button"):
        # Create a temporary file to download the edited JSON
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp.write(json.dumps(edited_resume, indent=2).encode())
            tmp_path = tmp.name
        
        # Offer download
        with open(tmp_path, "rb") as f:
            st.download_button(
                label="Download Edited Resume JSON",
                data=f,
                file_name="edited_resume.json",
                mime="application/json",
                key="download_json_button"
            )
        
        # Clean up the temp file
        os.unlink(tmp_path)
    
    return edited_resume

# Initialize session state
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# Function to update active tab and provide guidance
def update_active_tab(new_tab_index):
    st.session_state.active_tab = new_tab_index
    st.success(f"✅ Step {new_tab_index} completed! Please click on the '{tab_titles[new_tab_index]}' tab to continue.")

# Main app
st.set_page_config(page_title="Portfolio Builder", layout="wide")
st.title("🌐 Resume → Portfolio Website Generator")

# Create tabs for workflow
tab_titles = ["1. Upload & Edit", "2. Choose Theme", "3. Preview & Deploy"]
tabs = st.tabs(tab_titles)

with tabs[0]:  # Upload & Edit tab
    resume_file = st.file_uploader("Upload Resume JSON", type=["json"], key="resume_uploader")
    
    if resume_file:
        try:
            # Load and store resume data in session state
            if "resume_data" not in st.session_state:
                resume_data = json.load(resume_file)
                st.session_state.resume_data = resume_data
                st.success("Resume JSON loaded successfully! You can now edit your information.")
            
            # Edit resume data
            st.session_state.edited_resume = edit_resume_data(st.session_state.resume_data)
            
            # Button to proceed to theme selection
            if st.button("Continue to Theme Selection", key="continue_to_themes"):
                update_active_tab(1)
                
        except json.JSONDecodeError:
            st.error("Error: The uploaded file is not a valid JSON.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload your resume JSON file to get started.")

with tabs[1]:  # Choose Theme tab
    if st.session_state.active_tab == 1 and "edited_resume" in st.session_state:
        display_theme_selector()
        
        if st.session_state.get("theme_selected", False):
            st.success(f"You have selected **{st.session_state.selected_theme}**")
            if st.button("Continue to Preview & Deploy", key="continue_to_deploy"):
                update_active_tab(2)
    else:
        if st.session_state.active_tab < 1:
            st.warning("Please complete step 1 (Upload & Edit) first.")
        else:
            st.warning("Please upload and edit your resume first.")
with tabs[2]:  # Preview & Deploy tab
    if st.session_state.active_tab >= 2 and "edited_resume" in st.session_state and "selected_theme" in st.session_state:
        st.subheader("Final Review")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Your Information")
            st.write(f"**Theme Selected**: {st.session_state.selected_theme}")
            
            # Get username from the correct structure
            if "name" in st.session_state.edited_resume:
                username = st.session_state.edited_resume["name"]
            elif "personal_info" in st.session_state.edited_resume and "name" in st.session_state.edited_resume["personal_info"]:
                username = st.session_state.edited_resume["personal_info"]["name"]
            else:
                username = "portfolio"
            
            st.write(f"**Portfolio Owner**: {username}")
            
            # Display deployment button
            if st.button("🚀 Generate & Deploy Portfolio", key="final_deploy_button"):
                with st.spinner("Processing and deploying your portfolio..."):
                    try:
                        # Render HTML
                        html = render_html(
                            st.session_state.edited_resume,
                            THEMES[st.session_state.selected_theme]['file']
                        )
                        
                        # Deploy to GitHub
                        url = create_github_repo(
                            username,
                            html,
                            st.session_state.edited_resume,
                            THEMES[st.session_state.selected_theme]['file']
                        )
                        
                        if url:
                            st.success(f"✅ Portfolio successfully deployed! View it here: [🔗 {url}]({url})")
                            st.balloons()
                            
                            # Reset for a new portfolio
                            if st.button("Create Another Portfolio", key="reset_app"):
                                for key in ["resume_data", "edited_resume", "selected_theme", "active_tab"]:
                                    if key in st.session_state:
                                        del st.session_state[key]
                                st.write("Please refresh the page to start over.")
                    except Exception as e:
                        st.error(f"Error deploying portfolio: {str(e)}")
        
        with col2:
            # Offer JSON download
            st.markdown("### Download Your Edited Resume")
            if st.button("Download Edited JSON", key="download_final_json"):
                # Create a temporary file to download the edited JSON
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                    tmp.write(json.dumps(st.session_state.edited_resume, indent=2).encode())
                    tmp_path = tmp.name
                
                # Offer download
                with open(tmp_path, "rb") as f:
                    st.download_button(
                        label="Download JSON File",
                        data=f,
                        file_name="edited_resume.json",
                        mime="application/json",
                        key="download_final_json_button"
                    )
                
                # Clean up
                os.unlink(tmp_path)
    else:
        if st.session_state.active_tab < 2:
            st.warning(f"Please complete steps 1-2 first before deploying.")
        else:
            st.warning("Please upload your resume, edit it, and select a theme first.")

# Display current step progress
current_step = st.session_state.active_tab + 1
total_steps = 3
st.sidebar.progress(current_step / total_steps)
st.sidebar.write(f"**Current Progress**: Step {current_step} of {total_steps}")
st.sidebar.write(f"**Current Step**: {tab_titles[st.session_state.active_tab]}")

# Add next step instructions
if st.session_state.active_tab < 2:
    next_step = tab_titles[st.session_state.active_tab + 1]
    st.sidebar.info(f"**Next step**: {next_step}")










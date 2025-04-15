

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
import google.generativeai as genai
import time

load_dotenv()

# Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "backend" / "templates"

# Set up the correct path to your images
PREVIEW_DIR = Path(__file__).parent.parent / "backend" / "static" / "images"
os.makedirs(PREVIEW_DIR, exist_ok=True)

# Define themes with descriptions
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

# Gemini System Prompt for Resume Editing (as a regular prompt, not a system prompt)
RESUME_EDITOR_INSTRUCTIONS = """
You are a resume assistant that helps users edit their portfolio JSON data. 
Your task is to update a JSON resume based on the user's instructions.

The JSON resume has the following structure:
{
  "about": {
    "name": "Full Name",
    "location": "City, State",
    "email": "email@example.com",
    "phone": "Phone number",
    "linkedin_hyperlink": "LinkedIn URL",
    "github_hyperlink": "GitHub URL",
    "summary": "Professional summary paragraph"
  },
  "education": [
    {
      "university": "University Name",
      "location": "University Location",
      "degree": "Degree Name",
      "period": "Month Year - Month Year",
      "related_coursework": ["Course 1", "Course 2", "Course 3"],
      "gpa": "GPA Value"
    }
  ],
  "skills": [
    {
      "category": "Category Name",
      "skills": ["Skill 1", "Skill 2", "Skill 3"]
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "position": "Job Title",
      "location": "Job Location",
      "period": "Month Year - Month Year",
      "responsibilities": ["Responsibility 1", "Responsibility 2", "Responsibility 3"]
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "Project description",
      "technologies": ["Tech 1", "Tech 2", "Tech 3"],
      "url": "Project URL"
    }
  ],
  "accomplishments": [
    {
      "title": "Accomplishment Title",
      "date": "Month Year",
      "link": "Relevant URL"
    }
  ]
}

Follow these rules:
1. Maintain the exact JSON structure - do not add or remove any top-level keys
2. Format dates consistently as "Month Year" (e.g., "January 2023")
3. Return ONLY valid JSON without any other text or explanations
4. Make sure comma placement is correct and the JSON will parse properly
5. Preserve information that the user doesn't explicitly ask to change
6. Use proper capitalization and professional language
7. For lists (like skills, responsibilities), maintain them as valid JSON arrays
8. If adding a new item to an array (like a new job or project), follow the same structure as existing items

If the user asks to add a new entry (education, job, project, etc.), create a complete entry with all required fields.
If any fields would be empty, use reasonable placeholder text that the user can edit later.
"""

def render_html(resume_json, template_file):
    """Render HTML template with resume data"""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_file)
    return template.render(resume=resume_json)

def create_github_repo(repo_name, html_content, resume_json, template_file):
    """Create and deploy GitHub repository with portfolio"""
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    #repo_name = f"{username.replace(' ', '-').lower()}-portfolio"
    
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
                pass
        
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

def display_resume_json(resume_data):
    """Display the resume data in a readable format"""
    
    # Create a unique key for the container to force rerendering
    if "preview_key" not in st.session_state:
        st.session_state.preview_key = 0
    
    # Increment the key each time we display to force refreshing
    st.session_state.preview_key += 1
    
    # Use a container with the unique key to force redrawing
    with st.container(key=f"preview_container_{st.session_state.preview_key}"):
        # About section
        if "about" in resume_data:
            about = resume_data["about"]
            st.subheader("📋 Personal Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {about.get('name', 'Not specified')}")
                st.markdown(f"**Email:** {about.get('email', 'Not specified')}")
                st.markdown(f"**Phone:** {about.get('phone', 'Not specified')}")
            with col2:
                st.markdown(f"**Location:** {about.get('location', 'Not specified')}")
                st.markdown(f"**LinkedIn:** {about.get('linkedin_hyperlink', 'Not specified')}")
                st.markdown(f"**GitHub:** {about.get('github_hyperlink', 'Not specified')}")
            
            if "summary" in about:
                st.markdown(f"**Summary:** {about['summary']}")
            
            st.markdown("---")
        
        # Education section
        if "education" in resume_data and resume_data["education"]:
            st.subheader("🎓 Education")
            for i, edu in enumerate(resume_data["education"]):
                with st.expander(f"{edu.get('university', 'University')} - {edu.get('degree', 'Degree')}"):
                    st.markdown(f"**University:** {edu.get('university', 'Not specified')}")
                    st.markdown(f"**Location:** {edu.get('location', 'Not specified')}")
                    st.markdown(f"**Degree:** {edu.get('degree', 'Not specified')}")
                    st.markdown(f"**Period:** {edu.get('period', 'Not specified')}")
                    
                    if "gpa" in edu:
                        st.markdown(f"**GPA:** {edu['gpa']}")
                    
                    if "related_coursework" in edu and edu["related_coursework"]:
                        st.markdown("**Related Coursework:**")
                        for course in edu["related_coursework"]:
                            st.markdown(f"- {course}")
            
            st.markdown("---")
        
        # Skills section
        if "skills" in resume_data and resume_data["skills"]:
            st.subheader("🔧 Skills")
            for skill_group in resume_data["skills"]:
                with st.expander(skill_group.get("category", "Skills")):
                    if "skills" in skill_group and skill_group["skills"]:
                        st.markdown(", ".join(skill_group["skills"]))
            
            st.markdown("---")
        
        # Experience section
        if "experience" in resume_data and resume_data["experience"]:
            st.subheader("💼 Work Experience")
            for i, exp in enumerate(resume_data["experience"]):
                with st.expander(f"{exp.get('position', 'Position')} at {exp.get('company', 'Company')}"):
                    st.markdown(f"**Company:** {exp.get('company', 'Not specified')}")
                    st.markdown(f"**Position:** {exp.get('position', 'Not specified')}")
                    st.markdown(f"**Period:** {exp.get('period', 'Not specified')}")
                    st.markdown(f"**Location:** {exp.get('location', 'Not specified')}")
                    
                    if "responsibilities" in exp and exp["responsibilities"]:
                        st.markdown("**Responsibilities:**")
                        for resp in exp["responsibilities"]:
                            st.markdown(f"- {resp}")
            
            st.markdown("---")
        
        # Projects section
        if "projects" in resume_data and resume_data["projects"]:
            st.subheader("🚀 Projects")
            for i, proj in enumerate(resume_data["projects"]):
                with st.expander(proj.get("name", "Project")):
                    st.markdown(f"**Name:** {proj.get('name', 'Not specified')}")
                    st.markdown(f"**Description:** {proj.get('description', 'Not specified')}")
                    
                    if "url" in proj and proj["url"]:
                        st.markdown(f"**URL:** {proj['url']}")
                    
                    if "technologies" in proj and proj["technologies"]:
                        st.markdown("**Technologies:**")
                        st.markdown(", ".join(proj["technologies"]))
            
            st.markdown("---")
        
        # Accomplishments section
        if "accomplishments" in resume_data and resume_data["accomplishments"]:
            st.subheader("🏆 Accomplishments")
            for i, accom in enumerate(resume_data["accomplishments"]):
                with st.expander(accom.get("title", "Accomplishment")):
                    st.markdown(f"**Title:** {accom.get('title', 'Not specified')}")
                    st.markdown(f"**Date:** {accom.get('date', 'Not specified')}")
                    
                    if "link" in accom and accom["link"]:
                        st.markdown(f"**Link:** {accom['link']}")
            
            st.markdown("---")

def create_llm_based_editor(resume_data):
    """Create an LLM-based chat editor for resume data"""
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI resume editor. Please tell me what changes you'd like to make to your resume. You can say things like:\n\n- Update my job title at Google to 'Senior Software Engineer'\n- Add a new project called 'Portfolio Generator'\n- Update my skills to include 'React', 'Node.js', and 'Python'\n- Add a new work experience"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input
    if prompt := st.chat_input("What would you like to edit in your resume?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Prepare the context for Gemini
        resume_json_str = json.dumps(resume_data, indent=2)
        
        # Set up Gemini model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        # Build the prompt with instructions
        full_prompt = f"""
{RESUME_EDITOR_INSTRUCTIONS}

Here is my current resume JSON:
```json
{resume_json_str}
```

Edit request: {prompt}

Please provide only the updated JSON.
"""
        
        # Show spinner while processing
        with st.spinner("Updating your resume..."):
            try:
                # Get response without using system prompts
                response = model.generate_content(full_prompt)
                
                # Extract the JSON from the response
                response_text = response.text
                
                # Try to parse the response as JSON
                try:
                    # Find JSON content in the response if it's wrapped in backticks
                    if "```json" in response_text:
                        json_content = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        json_content = response_text.split("```")[1].strip()
                    else:
                        json_content = response_text
                    
                    # Parse JSON
                    updated_resume = json.loads(json_content)
                    
                    # Update session state with the updated resume
                    st.session_state.edited_resume = updated_resume
                    
                    # Set a flag to indicate the resume was updated
                    st.session_state.resume_updated = True
                    
                    # Create assistant response
                    assistant_response = "✅ I've updated your resume! Here's what changed:\n\n"
                    
                    # Identify the changes (simplified version)
                    if "about" in prompt.lower():
                        assistant_response += "- Updated your personal information\n"
                    if "education" in prompt.lower() or "university" in prompt.lower() or "degree" in prompt.lower():
                        assistant_response += "- Updated your education details\n"
                    if "skill" in prompt.lower():
                        assistant_response += "- Updated your skills\n"
                    if "experience" in prompt.lower() or "job" in prompt.lower() or "work" in prompt.lower():
                        assistant_response += "- Updated your work experience\n"
                    if "project" in prompt.lower():
                        assistant_response += "- Updated your projects\n"
                    if "accomplishment" in prompt.lower() or "award" in prompt.lower() or "certification" in prompt.lower():
                        assistant_response += "- Updated your accomplishments\n"
                    
                    assistant_response += "\nYou can see the changes in the resume preview. Is there anything else you'd like to update?"
                    
                except json.JSONDecodeError:
                    # If can't parse as JSON, show error and original response
                    st.error("I couldn't generate valid JSON. Please try a different request.")
                    assistant_response = f"I had trouble updating your resume. Could you please rephrase your request? Here's what I tried to do:\n\n{response_text}"
                    
                    # Keep the original resume
                    st.session_state.edited_resume = resume_data
                    st.session_state.resume_updated = False
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
                assistant_response = "I encountered an error while trying to update your resume. Please try again."
                st.session_state.edited_resume = resume_data
                st.session_state.resume_updated = False
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(assistant_response)
        
        # Force a rerun to update the preview
        st.rerun()
    
    return st.session_state.edited_resume

# Initialize session state
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

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
                st.session_state.edited_resume = copy.deepcopy(resume_data)
                st.success("Resume JSON loaded successfully! You can now edit your information.")
            
            # Display the current resume data (read-only) and chat editor
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Current Resume Preview")
                display_resume_json(st.session_state.edited_resume)
            
            with col2:
                st.subheader("AI Resume Editor")
                # LLM-based editor
                create_llm_based_editor(st.session_state.edited_resume)
                
            # Button to proceed to theme selection
            if st.button("Continue to Theme Selection", key="continue_to_themes"):
                st.session_state.active_tab = 1
                st.success(f"✅ Step 1 completed! Please click on the '2. Choose Theme' tab to continue.")
                
        except json.JSONDecodeError:
            st.error("Error: The uploaded file is not a valid JSON.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload your resume JSON file to get started.")
        
        # Example JSON
        example_json = {
            "about": {
                "name": "Alex Carter",
                "location": "San Francisco, CA",
                "email": "alex.carter@example.com",
                "phone": "+1-555-123-4567",
                "linkedin_hyperlink": "https://linkedin.com/in/alexcarter",
                "github_hyperlink": "https://github.com/alexcarter",
                "summary": "Passionate software engineer with 3+ years of experience in building scalable web applications and backend systems."
            },
            "education": [
                {
                    "university": "Stanford University",
                    "location": "Stanford, CA",
                    "degree": "Master of Science in Computer Science",
                    "period": "Sep 2020 - Jun 2022",
                    "related_coursework": ["Machine Learning", "Distributed Systems", "Database Design"],
                    "gpa": "3.9"
                }
            ],
            "skills": [
                {
                    "category": "Programming Languages",
                    "skills": ["Python", "JavaScript", "C++"]
                }
            ],
            "experience": [
                {
                    "company": "TechNova Inc.",
                    "position": "Backend Developer",
                    "location": "Remote",
                    "period": "Jul 2022 - Present",
                    "responsibilities": ["Developed RESTful APIs with FastAPI and integrated with PostgreSQL and Redis."]
                }
            ],
            "projects": [
                {
                    "name": "AI-Powered Resume Parser",
                    "description": "Built a FastAPI-based application that parses and analyzes resumes using spaCy and OpenAI.",
                    "technologies": ["Python", "FastAPI", "spaCy", "OpenAI"],
                    "url": "https://github.com/alexcarter/resume-parser"
                }
            ],
            "accomplishments": [
                {
                    "title": "Winner - Hack the Bay 2023",
                    "date": "Mar 2023",
                    "link": "https://devpost.com/software/ai-nurse"
                }
            ]
        }
        
        st.expander("See Example JSON Format").code(json.dumps(example_json, indent=2))

with tabs[1]:  # Choose Theme tab
    if st.session_state.active_tab >= 1 and "edited_resume" in st.session_state:
        display_theme_selector()
        
        if st.session_state.get("theme_selected", False):
            st.success(f"You have selected **{st.session_state.selected_theme}**")
            if st.button("Continue to Preview & Deploy", key="continue_to_deploy"):
                st.session_state.active_tab = 2
                st.success(f"✅ Step 2 completed! Please click on the '3. Preview & Deploy' tab to continue.")
    else:
        if st.session_state.active_tab < 1:
            st.warning("Please complete step 1 (Upload & Edit) first.")
        else:
            st.warning("Please upload and edit your resume first.")

with tabs[2]:  # Preview & Deploy tab
    if st.session_state.active_tab >= 2 and "edited_resume" in st.session_state and st.session_state.get("theme_selected", False):
        st.subheader("Final Review")
        
        # Get username from the correct structure based on new JSON format
        if "about" in st.session_state.edited_resume and "name" in st.session_state.edited_resume["about"]:
            username = st.session_state.edited_resume["about"]["name"]
        else:
            username = "portfolio"
            
        # Display information
        st.markdown("### Your Information")
        st.write(f"**Theme Selected**: {st.session_state.selected_theme}")
        st.write(f"**Portfolio Owner**: {username}")

        st.subheader("Repository Configuration")
        repo_name_input = st.text_input("Enter the GitHub repository name you'd like to use", key="repo_name_input")

        # Validation state
        if "repo_valid" not in st.session_state:
            st.session_state.repo_valid = None
        
        #validate repo name

        if repo_name_input and not st.session_state.get("deployed_clicked", False):
                g =  Github(GITHUB_TOKEN)
                try:
                    g.get_user().get_repo(repo_name_input)
                    st.session_state.repo_valid = False
                    #st.error(f"A repository named '{repo_name_input}' already exists under your GitHub account. Please choose another name.")

                except:
                    st.session_state.repo_valid = True
                    #st.success("Repository name is available!")

        # Show validation message only before deployment
        if repo_name_input and not st.session_state.get("deploy_clicked", False):
            if st.session_state.repo_valid:
                st.success("Repository name available!")
            else:
                st.error(f"A repository named '{repo_name_input}' already exists under your GitHub account. Please choose another name.")

        # Display deployment options
        st.subheader("Deployment Options")
        
        # GitHub Deployment
        if "deploy_clicked" not in st.session_state:
            st.session_state.deploy_clicked = False
            
        if "deployment_url" not in st.session_state:
            st.session_state.deployment_url = None
            
        if not st.session_state.deploy_clicked:
            if st.button("🚀 Deploy to GitHub Pages", key="github_deploy_button"):
                if not repo_name_input:
                     st.error("Please enter a GitHub repository name before deploying.")
                elif st.session_state.repo_valid is not True:
                    st.error("Repository name is not valid. Please choose a unique name.")
                else:
                    st.session_state.deploy_clicked = True
                    html = render_html(
                        st.session_state.edited_resume,
                        THEMES[st.session_state.selected_theme]['file']
                     )
                #st.session_state.deploy_clicked = True
                    with st.spinner("Creating repository and uploading files..."):
                        try:
                            url = create_github_repo(
                            repo_name_input.strip(),
                            html,
                            st.session_state.edited_resume,
                            THEMES[st.session_state.selected_theme]['file']
                            )
                    
                            if url:
                                st.session_state.deployment_url = url
                                st.info("Repository created! Waiting for GitHub Pages to deploy (about 40 seconds)...")
                                st.rerun()

                        except Exception as e:
                            st.error(f"Error deploying portfolio: {str(e)}")
                            st.session_state.deploy_clicked = False


                    
                # Render HTML
                html = render_html(
                    st.session_state.edited_resume,
                    THEMES[st.session_state.selected_theme]['file']
                )
                
                # Deploy to GitHub
                with st.spinner("Creating repository and uploading files..."):
                    try:
                        url = create_github_repo(
                            username,
                            html,
                            st.session_state.edited_resume,
                            THEMES[st.session_state.selected_theme]['file']
                        )
                        
                        if url:
                            st.session_state.deployment_url = url
                            # Start the 15-second wait
                            st.info("Repository created! Waiting for GitHub Pages to deploy (about 15 seconds)...")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error deploying portfolio: {str(e)}")
                        st.session_state.deploy_clicked = False
        else:
            # Display a loading message with progress for 40 seconds
            if st.session_state.deployment_url:
                with st.spinner("GitHub Pages deployment in progress..."):
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    for i in range(100):
                        # Update every ~150ms to complete in ~40 seconds
                        time.sleep(0.40)
                        progress_bar.progress(i + 1)
                
                # After the progress is complete, show success message
                st.success(f"✅ Portfolio successfully deployed! View it here: [🔗 {st.session_state.deployment_url}]({st.session_state.deployment_url})")
                st.balloons()
                
                # Offer JSON download
                st.markdown("### Download Your Edited Resume")
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
                st.error("Deployment failed. Please try again.")
                st.session_state.deploy_clicked = False
    else:
        if st.session_state.active_tab < 2:
            st.warning(f"Please complete steps 1-2 first before deploying.")
        elif not st.session_state.get("theme_selected", False):
            st.warning("Please select a theme first.")
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
































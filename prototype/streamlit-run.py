# # app.py (Streamlit Frontend)
# import streamlit as st
# import requests
# import json
# import pandas as pd
# from io import StringIO

# # Set the title and configure the page
# st.set_page_config(
#     page_title="Resume Parser",
#     page_icon="📄",
#     layout="wide"
# )

# # Define the API endpoint
# API_URL = "http://localhost:8000"  # Adjust if your FastAPI is running elsewhere

# def main():
#     st.title("Resume Parser Application")
#     st.write("Upload a resume (PDF, DOCX, or TXT) to parse and store in markdown format.")
    
#     # Create tabs for different functionality
#     tabs = st.tabs(["Upload Resume", "View Resumes"])
    
#     # Upload tab
#     with tabs[0]:
#         upload_resume()
    
#     # View tab
#     with tabs[1]:
#         view_resumes()

# def upload_resume():
#     # File uploader
#     uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx", "txt"])
    
#     if uploaded_file is not None:
#         # Show a spinner while processing
#         with st.spinner("Processing resume..."):
#             # Create a requests file object
#             files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
#             try:
#                 # Send the file to the API
#                 response = requests.post(f"{API_URL}/upload/", files=files)
                
#                 if response.status_code == 200:
#                     resume_data = response.json()
#                     st.success("Resume parsed successfully!")
                    
#                     # Display the parsed data
#                     display_resume(resume_data)
#                 else:
#                     st.error(f"Error: {response.status_code} - {response.text}")
#             except requests.exceptions.ConnectionError:
#                 st.error("Failed to connect to the API. Make sure the FastAPI backend is running.")

# def view_resumes():
#     st.subheader("Previously Parsed Resumes")
    
#     try:
#         # Get all resumes from the API
#         response = requests.get(f"{API_URL}/resumes/")
        
#         if response.status_code == 200:
#             resume_list = response.json()["resumes"]
            
#             if resume_list:
#                 # Create a simple table with resume names
#                 resumes_df = pd.DataFrame([
#                     {"Resume ID": r["resume_id"], 
#                      "Name": r["metadata"]["name"] if r["metadata"]["name"] else "Unknown",
#                      "Email": r["metadata"]["contact"]["email"] if r["metadata"]["contact"]["email"] else "Unknown"}
#                     for r in resume_list
#                 ])
                
#                 st.dataframe(resumes_df)
                
#                 # Select a resume to view
#                 selected_resume_id = st.selectbox(
#                     "Select a resume to view",
#                     options=[r["resume_id"] for r in resume_list],
#                     format_func=lambda x: next((r["metadata"]["name"] for r in resume_list if r["resume_id"] == x), x)
#                 )
                
#                 if selected_resume_id:
#                     selected_resume = next((r for r in resume_list if r["resume_id"] == selected_resume_id), None)
#                     if selected_resume:
#                         display_resume(selected_resume)
#             else:
#                 st.info("No resumes have been parsed yet.")
#         else:
#             st.error(f"Error: {response.status_code} - {response.text}")
#     except requests.exceptions.ConnectionError:
#         st.error("Failed to connect to the API. Make sure the FastAPI backend is running.")

# def display_resume(resume_data):
#     # Create columns for layout
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Parsed Information")
        
#         # Display basic info
#         st.write(f"**Name:** {resume_data['metadata']['name']}")
#         contact = resume_data['metadata']['contact']
#         st.write(f"**Email:** {contact['email']}")
#         st.write(f"**Phone:** {contact['phone']}")
        
#         # Education
#         if resume_data['metadata']['education']:
#             st.write("**Education:**")
#             for edu in resume_data['metadata']['education']:
#                 st.write(f"- {edu}")
        
#         # Experience
#         if resume_data['metadata']['experience']:
#             st.write("**Experience:**")
#             for exp in resume_data['metadata']['experience']:
#                 st.write(f"- {exp}")
        
#         # Skills
#         if resume_data['metadata']['skills']:
#             st.write("**Skills:**")
#             for skill in resume_data['metadata']['skills']:
#                 st.write(f"- {skill}")
    
#     with col2:
#         st.subheader("Markdown Output")
        
#         # Display the markdown
#         st.markdown(resume_data['markdown'])
        
#         # Provide a way to download the markdown
#         st.download_button(
#             label="Download Markdown",
#             data=resume_data['markdown'],
#             file_name=f"resume_{resume_data['resume_id']}.md",
#             mime="text/markdown"
#         )
        
#         # Option to view raw text
#         with st.expander("View Raw Text"):
#             st.text(resume_data['content'])

# if __name__ == "__main__":
#     main()


# app.py (Streamlit Frontend)
import streamlit as st
import requests
import json
import pandas as pd
from io import StringIO

# Set the title and configure the page
st.set_page_config(
    page_title="Resume Parser",
    page_icon="📄",
    layout="wide"
)

# Define the API endpoint
API_URL = "http://localhost:8000"  # Adjust if your FastAPI is running elsewhere

def main():
    st.title("Resume Parser Application")
    st.write("Upload a resume (PDF, DOCX, or TXT) to parse and store in markdown format.")
    
    # Create tabs for different functionality
    tabs = st.tabs(["Upload Resume", "View Resumes"])
    
    # Upload tab
    with tabs[0]:
        upload_resume()
    
    # View tab
    with tabs[1]:
        view_resumes()

def upload_resume():
    # File uploader
    uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        # Show a spinner while processing
        with st.spinner("Processing resume..."):
            # Create a requests file object
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            try:
                # Send the file to the API
                response = requests.post(f"{API_URL}/upload/", files=files)
                
                if response.status_code == 200:
                    resume_data = response.json()
                    st.success("Resume parsed successfully!")
                    
                    # Display the parsed data
                    display_resume(resume_data)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the API. Make sure the FastAPI backend is running.")

def view_resumes():
    st.subheader("Previously Parsed Resumes")
    
    try:
        # Get all resumes from the API
        response = requests.get(f"{API_URL}/resumes/")
        
        if response.status_code == 200:
            resume_list = response.json()["resumes"]
            
            if resume_list:
                # Create a simple table with resume names
                resumes_df = pd.DataFrame([
                    {"Resume ID": r["resume_id"], 
                     "Name": r["metadata"]["name"] if r["metadata"]["name"] else "Unknown",
                     "Email": r["metadata"]["contact"]["email"] if r["metadata"]["contact"]["email"] else "Unknown"}
                    for r in resume_list
                ])
                
                st.dataframe(resumes_df)
                
                # Select a resume to view
                selected_resume_id = st.selectbox(
                    "Select a resume to view",
                    options=[r["resume_id"] for r in resume_list],
                    format_func=lambda x: next((r["metadata"]["name"] for r in resume_list if r["resume_id"] == x), x)
                )
                
                if selected_resume_id:
                    selected_resume = next((r for r in resume_list if r["resume_id"] == selected_resume_id), None)
                    if selected_resume:
                        display_resume(selected_resume)
            else:
                st.info("No resumes have been parsed yet.")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the API. Make sure the FastAPI backend is running.")

def display_resume(resume_data):
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parsed Information")
        
        # Display name and contact info
        st.markdown(f"### {resume_data['metadata']['name']}")
        
        # Contact information
        contact = resume_data['metadata']['contact']
        contact_info = []
        if contact.get('email'): contact_info.append(f"📧 **Email:** {contact['email']}")
        if contact.get('phone'): contact_info.append(f"📱 **Phone:** {contact['phone']}")
        if contact.get('location'): contact_info.append(f"📍 **Location:** {contact['location']}")
        if contact.get('linkedin'): contact_info.append(f"🔗 **LinkedIn:** {contact['linkedin']}")
        
        for info in contact_info:
            st.markdown(info)
            
        # Education
        if resume_data['metadata'].get('education'):
            st.markdown("### 🎓 Education")
            for edu in resume_data['metadata']['education']:
                st.markdown(f"**{edu['institution']}**")
                if edu.get('degree'):
                    st.markdown(f"*{edu['degree']}*")
                if edu.get('dates'):
                    st.markdown(f"*{edu['dates']}*")
                
                for detail in edu.get('details', []):
                    st.markdown(f"- {detail}")
                st.markdown("---")
        
        # Experience
        if resume_data['metadata'].get('experience'):
            st.markdown("### 💼 Work Experience")
            for exp in resume_data['metadata']['experience']:
                st.markdown(f"**{exp['company']}**")
                if exp.get('position'):
                    st.markdown(f"*{exp['position']}*")
                
                location_date = []
                if exp.get('location'): location_date.append(exp['location'])
                if exp.get('dates'): location_date.append(exp['dates'])
                
                if location_date:
                    st.markdown(f"*{' | '.join(location_date)}*")
                
                for resp in exp.get('responsibilities', []):
                    st.markdown(f"- {resp}")
                st.markdown("---")
        
        # Skills
        if resume_data['metadata'].get('skills'):
            st.markdown("### 🔧 Skills")
            for skill in resume_data['metadata']['skills']:
                if ":" in skill:
                    category, skill_list = skill.split(":", 1)
                    st.markdown(f"**{category.strip()}:** {skill_list.strip()}")
                else:
                    st.markdown(f"- {skill}")
        
        # Projects
        if resume_data['metadata'].get('projects'):
            st.markdown("### 🚀 Projects")
            for project in resume_data['metadata']['projects']:
                project_header = f"**{project['title']}**"
                if project.get('date'):
                    project_header += f" *({project['date']})*"
                st.markdown(project_header)
                
                for desc in project.get('description', []):
                    st.markdown(f"- {desc}")
                st.markdown("---")
    
    with col2:
        st.subheader("Resume View")
        
        # Create tabs for different views
        view_tabs = st.tabs(["Markdown", "JSON", "Raw Text"])
        
        # Markdown tab
        with view_tabs[0]:
            st.markdown(resume_data['markdown'])
            
            st.download_button(
                label="Download Markdown",
                data=resume_data['markdown'],
                file_name=f"resume_{resume_data['resume_id']}.md",
                mime="text/markdown",
                key=f"markdown_download_{resume_data['resume_id']}"
            )
        
        # JSON tab
        with view_tabs[1]:
            # Create a clean JSON version for display and download
            json_data = resume_data['metadata'].copy()
            if 'raw_text' in json_data:
                del json_data['raw_text']
            
            formatted_json = json.dumps(json_data, indent=2)
            
            # Display JSON with syntax highlighting
            st.json(json_data)
            
            # Download button for JSON
            st.download_button(
                label="Download JSON",
                data=formatted_json,
                file_name=f"resume_{resume_data['resume_id']}.json",
                mime="application/json",
                key=f"json_download_{resume_data['resume_id']}"
            )
        
        # Raw text tab
        with view_tabs[2]:
            st.text_area("Raw Text Content", resume_data['content'], height=400)

if __name__ == "__main__":
    main()










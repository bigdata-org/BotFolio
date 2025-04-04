# # main.py (FastAPI Backend)
# import os
# import uuid
# from typing import Dict, List, Optional
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import uvicorn
# import PyPDF2
# import docx2txt
# import json
# from pathlib import Path

# # Create necessary directories
# UPLOAD_DIR = Path("uploads")
# PARSED_DIR = Path("parsed_resumes")
# UPLOAD_DIR.mkdir(exist_ok=True)
# PARSED_DIR.mkdir(exist_ok=True)

# app = FastAPI(title="Resume Parser API")

# # Add CORS middleware to allow Streamlit to access the API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ResumeData(BaseModel):
#     resume_id: str
#     content: str
#     metadata: Dict
#     markdown: str

# class ResumeList(BaseModel):
#     resumes: List[Dict]

# # In-memory database (for demo purposes - in production, use a real DB)
# parsed_resumes = {}

# def extract_text_from_pdf(file_path):
#     """Extract text from PDF files"""
#     text = ""
#     with open(file_path, "rb") as pdf_file:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         for page in pdf_reader.pages:
#             text += page.extract_text() + "\n"
#     return text

# def extract_text_from_docx(file_path):
#     """Extract text from DOCX files"""
#     return docx2txt.process(file_path)

# def extract_text_from_txt(file_path):
#     """Extract text from TXT files"""
#     with open(file_path, "r", encoding="utf-8", errors="ignore") as txt_file:
#         return txt_file.read()

# def parse_resume(text):
#     """
#     Simple resume parser
#     In a real application, you would use more sophisticated techniques like
#     NLP, regex patterns, or ML models for better extraction
#     """
#     # This is a simplified parser - in production, use a more robust solution
#     lines = text.split('\n')
    
#     # Basic extraction
#     name = lines[0] if lines else ""
#     email = next((line for line in lines if '@' in line), "")
#     phone = next((line for line in lines if any(p in line for p in ['+', '(', ')', '-']) and any(c.isdigit() for c in line)), "")
    
#     # Extract education (simplistic approach)
#     education_keywords = ['education', 'university', 'college', 'degree', 'bachelor', 'master', 'phd']
#     education = [line for line in lines if any(keyword in line.lower() for keyword in education_keywords)]
    
#     # Extract experience (simplistic approach)
#     experience_keywords = ['experience', 'work', 'job', 'position', 'employment']
#     experience = [line for line in lines if any(keyword in line.lower() for keyword in experience_keywords)]
    
#     # Extract skills (simplistic approach)
#     skill_keywords = ['skills', 'abilities', 'proficient', 'competent', 'experienced in']
#     skills = [line for line in lines if any(keyword in line.lower() for keyword in skill_keywords)]
    
#     result = {
#         "name": name,
#         "contact": {"email": email, "phone": phone},
#         "education": education,
#         "experience": experience,
#         "skills": skills,
#         "raw_text": text
#     }
    
#     # Generate markdown
#     markdown = f"# {name}\n\n"
#     markdown += f"**Contact:** {email} | {phone}\n\n"
    
#     if education:
#         markdown += "## Education\n\n"
#         for edu in education:
#             markdown += f"- {edu}\n"
#         markdown += "\n"
    
#     if experience:
#         markdown += "## Experience\n\n"
#         for exp in experience:
#             markdown += f"- {exp}\n"
#         markdown += "\n"
    
#     if skills:
#         markdown += "## Skills\n\n"
#         for skill in skills:
#             markdown += f"- {skill}\n"
    
#     return result, markdown

# @app.post("/upload/", response_model=ResumeData)
# async def upload_resume(file: UploadFile = File(...)):
#     """
#     Upload and process a resume file
#     """
#     # Generate a unique ID for the resume
#     resume_id = str(uuid.uuid4())
    
#     # Get file extension
#     file_extension = os.path.splitext(file.filename)[1].lower()
    
#     # Check if the file type is supported
#     if file_extension not in ['.pdf', '.docx', '.txt']:
#         raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, or TXT files.")
    
#     # Save the uploaded file
#     file_path = UPLOAD_DIR / f"{resume_id}{file_extension}"
#     with open(file_path, "wb") as buffer:
#         buffer.write(await file.read())
    
#     # Extract text based on file type
#     if file_extension == '.pdf':
#         text = extract_text_from_pdf(file_path)
#     elif file_extension == '.docx':
#         text = extract_text_from_docx(file_path)
#     else:  # .txt
#         text = extract_text_from_txt(file_path)
    
#     # Parse the resume text
#     parsed_data, markdown = parse_resume(text)
    
#     # Save the parsed resume
#     resume_data = {
#         "resume_id": resume_id,
#         "content": text,
#         "metadata": parsed_data,
#         "markdown": markdown
#     }
    
#     # Save to our in-memory database
#     parsed_resumes[resume_id] = resume_data
    
#     # Save to file for persistence
#     with open(PARSED_DIR / f"{resume_id}.json", "w") as json_file:
#         json.dump(resume_data, json_file)
    
#     return resume_data

# @app.get("/resumes/", response_model=ResumeList)
# async def get_all_resumes():
#     """
#     Get a list of all parsed resumes
#     """
#     return {"resumes": list(parsed_resumes.values())}

# @app.get("/resume/{resume_id}", response_model=ResumeData)
# async def get_resume(resume_id: str):
#     """
#     Get a specific parsed resume by ID
#     """
#     if resume_id not in parsed_resumes:
#         # Try to load from file
#         resume_path = PARSED_DIR / f"{resume_id}.json"
#         if resume_path.exists():
#             with open(resume_path, "r") as json_file:
#                 parsed_resumes[resume_id] = json.load(json_file)
#         else:
#             raise HTTPException(status_code=404, detail="Resume not found")
    
#     return parsed_resumes[resume_id]

# if __name__ == "__main__":
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


# # main.py (FastAPI Backend)
# import os
# import uuid
# import re
# from typing import Dict, List, Optional
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import uvicorn
# import PyPDF2
# import docx2txt
# import json
# from pathlib import Path

# # Create necessary directories
# UPLOAD_DIR = Path("uploads")
# PARSED_DIR = Path("parsed_resumes")
# UPLOAD_DIR.mkdir(exist_ok=True)
# PARSED_DIR.mkdir(exist_ok=True)

# app = FastAPI(title="Resume Parser API")

# # Add CORS middleware to allow Streamlit to access the API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ResumeData(BaseModel):
#     resume_id: str
#     content: str
#     metadata: Dict
#     markdown: str

# class ResumeList(BaseModel):
#     resumes: List[Dict]

# # In-memory database (for demo purposes - in production, use a real DB)
# parsed_resumes = {}

# def extract_text_from_pdf(file_path):
#     """Extract text from PDF files"""
#     text = ""
#     with open(file_path, "rb") as pdf_file:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         for page in pdf_reader.pages:
#             text += page.extract_text() + "\n"
#     return text

# def extract_text_from_docx(file_path):
#     """Extract text from DOCX files"""
#     return docx2txt.process(file_path)

# def extract_text_from_txt(file_path):
#     """Extract text from TXT files"""
#     with open(file_path, "r", encoding="utf-8", errors="ignore") as txt_file:
#         return txt_file.read()

# def parse_resume(text):
#     """
#     Advanced resume parser that identifies sections and extracts structured information
#     """
#     # Clean and prepare the text
#     lines = [line.strip() for line in text.split('\n') if line.strip()]
    
#     # Extract name (typically the first line of the resume)
#     name = lines[0] if lines else ""
    
#     # Extract contact information using regex
#     email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
#     phone_pattern = r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
#     linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
#     location_pattern = r'[A-Za-z]+\s*,\s*[A-Z]{2}'  # City, State format
    
#     email = next((re.search(email_pattern, line).group(0) for line in lines if re.search(email_pattern, line)), "")
#     phone = next((re.search(phone_pattern, line).group(0) for line in lines if re.search(phone_pattern, line)), "")
#     linkedin = next((re.search(linkedin_pattern, line).group(0) for line in lines if re.search(linkedin_pattern, line)), "LinkedIn" if "LinkedIn" in text else "")
#     location = next((re.search(location_pattern, line).group(0) for line in lines if re.search(location_pattern, line)), "")
    
#     # Define section headers for detection
#     section_patterns = {
#         'education': r'\b(EDUCATION|Education|Academic Background)\b',
#         'experience': r'\b(EXPERIENCE|Experience|WORK EXPERIENCE|Work Experience|Employment History)\b',
#         'skills': r'\b(SKILLS|Skills|TECHNICAL SKILLS|Technical Skills|TECHNOLOGIES)\b',
#         'projects': r'\b(PROJECTS|Projects|ACADEMIC PROJECTS|Academic Projects)\b'
#     }
    
#     # Find sections in the resume
#     section_indices = {}
#     for i, line in enumerate(lines):
#         for section, pattern in section_patterns.items():
#             if re.search(pattern, line):
#                 section_indices[section] = i
                
#     # Handle cases where sections might be detected through content
#     if 'projects' not in section_indices:
#         # Check if there's a line that likely indicates a projects section
#         for i, line in enumerate(lines):
#             if re.search(r'\b(Web Scraping|App Development|Data Analysis|Analytics Tool|Software Project)\b', line) and \
#                re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b', line):
#                 # This might be a project entry
#                 # Look back a few lines to find a potential section header
#                 for j in range(max(0, i-3), i):
#                     if re.search(r'\b(PROJECTS|Projects|ACADEMIC PROJECTS|Academic Projects)\b', lines[j]):
#                         section_indices['projects'] = j
#                         break
#                 if 'projects' not in section_indices:
#                     # If we couldn't find a header, consider this line the start of projects
#                     section_indices['projects'] = max(0, i-1)

#     # Sort sections by their appearance in the document
#     sorted_sections = sorted(section_indices.items(), key=lambda x: x[1])
    
#     # Extract content for each section
#     sections_content = {}
#     for i, (section, idx) in enumerate(sorted_sections):
#         # Determine the end index of this section (start of next section or end of document)
#         end_idx = sorted_sections[i+1][1] if i+1 < len(sorted_sections) else len(lines)
#         # Get the content (skip the section header)
#         sections_content[section] = lines[idx+1:end_idx]
    
#     # Process education section
#     education_entries = []
#     if 'education' in sections_content:
#         current_university = None
#         current_degree = None
#         current_dates = None
#         current_details = []
        
#         for line in sections_content['education']:
#             # Check if this is a university line
#             if re.search(r'\b(University|College|School|Institute)\b', line, re.IGNORECASE):
#                 # Save previous entry if exists
#                 if current_university:
#                     education_entries.append({
#                         "institution": current_university,
#                         "degree": current_degree,
#                         "dates": current_dates,
#                         "details": current_details
#                     })
                
#                 # Start new entry
#                 current_university = line
#                 current_degree = None
#                 current_dates = None
#                 current_details = []
#             elif current_university:
#                 # Check for degree information
#                 if re.search(r'\b(Bachelor|Master|PhD|Degree|BS|MS|BA|MBA)\b', line, re.IGNORECASE):
#                     current_degree = line
#                 # Check for dates
#                 elif re.search(r'\b(20\d{2}|19\d{2})\b', line):
#                     current_dates = line
#                 # Otherwise, it's additional details
#                 else:
#                     current_details.append(line)
        
#         # Add the last entry
#         if current_university:
#             education_entries.append({
#                 "institution": current_university,
#                 "degree": current_degree,
#                 "dates": current_dates,
#                 "details": current_details
#             })
    
#     # Process experience section
#     experience_entries = []
#     if 'experience' in sections_content:
#         current_company = None
#         current_position = None
#         current_location = None
#         current_dates = None
#         current_responsibilities = []
        
#         for line in sections_content['experience']:
#             # Check if this is a company line (typically contains location)
#             if (not line.startswith('•') and 
#                 (re.search(r'\b(Inc|LLC|Ltd|Corp|Company|Mumbai|Boston|New York|INDIA|USA)\b', line, re.IGNORECASE) or
#                  re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', line))):  # Look for proper nouns
                
#                 # Save previous entry if exists
#                 if current_company:
#                     experience_entries.append({
#                         "company": current_company,
#                         "position": current_position,
#                         "location": current_location,
#                         "dates": current_dates,
#                         "responsibilities": current_responsibilities
#                     })
                
#                 # Start new entry
#                 current_company = line
#                 current_position = None
#                 current_location = None
#                 current_dates = None
#                 current_responsibilities = []
                
#                 # Try to extract location from company line
#                 location_match = re.search(r'\b([A-Za-z\s]+,\s*[A-Z]{2}|[A-Za-z\s]+,\s*[A-Za-z]+)\b', line)
#                 if location_match:
#                     current_location = location_match.group(0)
                
#             # Check if this is a position line (often contains dates)
#             elif current_company and not line.startswith('•') and re.search(r'\b(Engineer|Developer|Manager|Analyst|Director)\b', line, re.IGNORECASE):
#                 current_position = line
                
#                 # Try to extract dates from position line
#                 date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\b', line)
#                 if date_match:
#                     current_dates = date_match.group(0)
                    
#             # Check if this is a bullet point (responsibility)
#             elif current_company and line.startswith('•'):
#                 current_responsibilities.append(line.replace('•', '').strip())
                
#             # If we have a company but no position yet, this might be the position line
#             elif current_company and not current_position:
#                 current_position = line
                
#                 # Try to extract dates
#                 date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\b', line)
#                 if date_match:
#                     current_dates = date_match.group(0)
        
#         # Add the last entry
#         if current_company:
#             experience_entries.append({
#                 "company": current_company,
#                 "position": current_position,
#                 "location": current_location,
#                 "dates": current_dates,
#                 "responsibilities": current_responsibilities
#             })
    
#     # Process skills section
#     skills = []
#     if 'skills' in sections_content:
#         for line in sections_content['skills']:
#             # Check for bullet points (• or - or *)
#             if line.startswith('•') or line.startswith('-') or line.startswith('*'):
#                 # Clean up the bullet point and add to skills
#                 skill_text = line.lstrip('•-* ').strip()
#                 skills.append(skill_text)
#             # Handle lines without bullet points but with colon (likely categories)
#             elif ':' in line:
#                 skills.append(line.strip())
#             # Handle lines without bullets or colons (might be a skill category header)
#             elif line.strip() and len(line.strip()) > 2:
#                 skills.append(line.strip())
    
#     # Process projects section
#     project_entries = []
#     if 'projects' in sections_content:
#         current_project = None
#         current_date = None
#         current_description = []
        
#         for line in sections_content['projects']:
#             # Check if this is a project title line (typically includes a date)
#             if (not line.startswith('•') and not line.startswith('-') and not line.startswith('*') and 
#                 re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\b', line, re.IGNORECASE)):
#                 # Save previous project if exists
#                 if current_project:
#                     project_entries.append({
#                         "title": current_project,
#                         "date": current_date,
#                         "description": current_description
#                     })
                
#                 # Extract date
#                 date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\b', line, re.IGNORECASE)
#                 if date_match:
#                     current_date = date_match.group(0)
#                     # Remove date from title
#                     current_project = line.replace(date_match.group(0), '').strip()
#                 else:
#                     current_project = line
#                     current_date = ""
                
#                 current_description = []
            
#             # Check if this is a bullet point for project description
#             elif current_project and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
#                 current_description.append(line.lstrip('•-* ').strip())
        
#         # Add the last project
#         if current_project:
#             project_entries.append({
#                 "title": current_project,
#                 "date": current_date,
#                 "description": current_description
#             })
    
#     # If no projects were found but there are likely project entries in the text (fallback method)
#     if not project_entries:
#         # Try to find project entries with a different approach
#         project_pattern = r'([A-Za-z\s&]+)(\s+)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+)(\d{4})'
#         project_matches = re.finditer(project_pattern, text)
        
#         for match in project_matches:
#             project_title = match.group(1).strip()
#             project_date = f"{match.group(3)} {match.group(5)}"
            
#             # Find bullet points following this project
#             start_pos = match.end()
#             end_pos = text.find("Jan", start_pos + 1)
#             if end_pos == -1:
#                 end_pos = len(text)
                
#             project_content = text[start_pos:end_pos]
#             description = []
            
#             # Extract bullet points
#             for line in project_content.split('\n'):
#                 line = line.strip()
#                 if line.startswith('•') or line.startswith('-') or line.startswith('*'):
#                     description.append(line.lstrip('•-* ').strip())
            
#             if project_title and description:
#                 project_entries.append({
#                     "title": project_title,
#                     "date": project_date,
#                     "description": description
#                 })

    
#     # Compile the result
#     result = {
#         "name": name,
#         "contact": {
#             "email": email,
#             "phone": phone,
#             "linkedin": linkedin,
#             "location": location
#         },
#         "education": education_entries,
#         "experience": experience_entries,
#         "skills": skills,
#         "projects": project_entries,
#         "raw_text": text
#     }
    
#     # Generate improved markdown
#     markdown = f"# {name}\n\n"
    
#     # Contact section
#     contact_items = []
#     if phone: contact_items.append(f"📱 {phone}")
#     if email: contact_items.append(f"📧 {email}")
#     if location: contact_items.append(f"📍 {location}")
#     if linkedin: contact_items.append(f"🔗 LinkedIn")
    
#     markdown += f"**Contact:** {' | '.join(contact_items)}\n\n"
    
#     # Education section
#     if education_entries:
#         markdown += "## 🎓 Education\n\n"
#         for edu in education_entries:
#             markdown += f"### {edu['institution']}\n"
#             if edu.get('degree'):
#                 markdown += f"**{edu['degree']}**\n"
#             if edu.get('dates'):
#                 markdown += f"*{edu['dates']}*\n"
#             for detail in edu.get('details', []):
#                 markdown += f"- {detail}\n"
#             markdown += "\n"
    
#     # Experience section
#     if experience_entries:
#         markdown += "## 💼 Experience\n\n"
#         for exp in experience_entries:
#             markdown += f"### {exp['company']}\n"
#             if exp.get('position'):
#                 markdown += f"**{exp['position']}**\n"
            
#             location_date = []
#             if exp.get('location'): location_date.append(exp['location'])
#             if exp.get('dates'): location_date.append(exp['dates'])
            
#             if location_date:
#                 markdown += f"*{' | '.join(location_date)}*\n\n"
            
#             for resp in exp.get('responsibilities', []):
#                 markdown += f"- {resp}\n"
#             markdown += "\n"
    
#     # Skills section
#     if skills:
#         markdown += "## 🔧 Skills\n\n"
        
#         # Group skills by category if they follow "Category: skill1, skill2" pattern
#         current_category = None
        
#         for skill in skills:
#             if ":" in skill:
#                 # This is a category with skills list
#                 category, skill_list = skill.split(":", 1)
#                 markdown += f"**{category.strip()}:** {skill_list.strip()}\n\n"
#                 current_category = category.strip()
#             elif skill.strip() and all(c.isupper() or c.isspace() for c in skill):
#                 # This is likely a category header (all caps)
#                 markdown += f"### {skill}\n"
#                 current_category = skill
#             else:
#                 # This is a regular skill item
#                 markdown += f"- {skill}\n"
    
#     # Projects section
#     if project_entries:
#         markdown += "## 🚀 Projects\n\n"
#         for project in project_entries:
#             markdown += f"### {project['title']}"
#             if project.get('date'):
#                 markdown += f" *({project['date']})*"
#             markdown += "\n"
            
#             for detail in project.get('description', []):
#                 markdown += f"- {detail}\n"
#             markdown += "\n"
    
#     return result, markdown

# @app.post("/upload/", response_model=ResumeData)
# async def upload_resume(file: UploadFile = File(...)):
#     """
#     Upload and process a resume file
#     """
#     # Generate a unique ID for the resume
#     resume_id = str(uuid.uuid4())
    
#     # Get file extension
#     file_extension = os.path.splitext(file.filename)[1].lower()
    
#     # Check if the file type is supported
#     if file_extension not in ['.pdf', '.docx', '.txt']:
#         raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, or TXT files.")
    
#     # Save the uploaded file
#     file_path = UPLOAD_DIR / f"{resume_id}{file_extension}"
#     with open(file_path, "wb") as buffer:
#         buffer.write(await file.read())
    
#     # Extract text based on file type
#     if file_extension == '.pdf':
#         text = extract_text_from_pdf(file_path)
#     elif file_extension == '.docx':
#         text = extract_text_from_docx(file_path)
#     else:  # .txt
#         text = extract_text_from_txt(file_path)
    
#     # Parse the resume text
#     parsed_data, markdown = parse_resume(text)
    
#     # Save the parsed resume
#     resume_data = {
#         "resume_id": resume_id,
#         "content": text,
#         "metadata": parsed_data,
#         "markdown": markdown
#     }
    
#     # Save to our in-memory database
#     parsed_resumes[resume_id] = resume_data
    
#     # Save to file for persistence
#     with open(PARSED_DIR / f"{resume_id}.json", "w") as json_file:
#         json.dump(resume_data, json_file)
    
#     return resume_data

# @app.get("/resumes/", response_model=ResumeList)
# async def get_all_resumes():
#     """
#     Get a list of all parsed resumes
#     """
#     return {"resumes": list(parsed_resumes.values())}

# @app.get("/resume/{resume_id}", response_model=ResumeData)
# async def get_resume(resume_id: str):
#     """
#     Get a specific parsed resume by ID
#     """
#     if resume_id not in parsed_resumes:
#         # Try to load from file
#         resume_path = PARSED_DIR / f"{resume_id}.json"
#         if resume_path.exists():
#             with open(resume_path, "r") as json_file:
#                 parsed_resumes[resume_id] = json.load(json_file)
#         else:
#             raise HTTPException(status_code=404, detail="Resume not found")
    
#     return parsed_resumes[resume_id]

# if __name__ == "__main__":
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)



# import os
# import uuid
# import re
# from typing import Dict, List, Optional
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import uvicorn
# import PyPDF2
# import docx2txt
# import json
# from pathlib import Path

# # Create necessary directories
# UPLOAD_DIR = Path("uploads")
# PARSED_DIR = Path("parsed_resumes")
# UPLOAD_DIR.mkdir(exist_ok=True)
# PARSED_DIR.mkdir(exist_ok=True)

# app = FastAPI(title="Resume Parser API")

# # Add CORS middleware to allow Streamlit to access the API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ResumeData(BaseModel):
#     resume_id: str
#     content: str
#     metadata: Dict
#     markdown: str

# class ResumeList(BaseModel):
#     resumes: List[Dict]

# # In-memory database (for demo purposes - in production, use a real DB)
# parsed_resumes = {}

# def extract_text_from_pdf(file_path):
#     """Extract text from PDF files"""
#     text = ""
#     with open(file_path, "rb") as pdf_file:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         for page in pdf_reader.pages:
#             text += page.extract_text() + "\n"
#     return text

# def extract_text_from_docx(file_path):
#     """Extract text from DOCX files"""
#     return docx2txt.process(file_path)

# def extract_text_from_txt(file_path):
#     """Extract text from TXT files"""
#     with open(file_path, "r", encoding="utf-8", errors="ignore") as txt_file:
#         return txt_file.read()

# def parse_resume(text):
#     """
#     Advanced resume parser that identifies sections and extracts structured information
#     including links for LinkedIn, GitHub, and other URLs
#     """
#     # Clean and prepare the text
#     lines = [line.strip() for line in text.split('\n') if line.strip()]
    
#     # Extract name (typically the first line of the resume)
#     name = lines[0] if lines else ""
    
#     # Extract contact information using regex
#     email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
#     phone_pattern = r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    
#     # Enhanced patterns for social and professional links
#     linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
#     github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+'
#     portfolio_pattern = r'(?:https?://)?(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}(?:/[^\s]*)?'
#     location_pattern = r'[A-Za-z]+\s*,\s*[A-Z]{2}'  # City, State format
    
#     email = next((re.search(email_pattern, line).group(0) for line in lines if re.search(email_pattern, line)), "")
#     phone = next((re.search(phone_pattern, line).group(0) for line in lines if re.search(phone_pattern, line)), "")
    
#     # Extract LinkedIn URL
#     linkedin = next((re.search(linkedin_pattern, line).group(0) for line in lines if re.search(linkedin_pattern, line)), "")
#     # If no LinkedIn URL found but "LinkedIn" word exists, mark it for later handling
#     if not linkedin and any("linkedin" in line.lower() for line in lines):
#         linkedin = "LinkedIn mentioned without URL"
    
#     # Extract GitHub URL
#     github = next((re.search(github_pattern, line).group(0) for line in lines if re.search(github_pattern, line)), "")
#     # If no GitHub URL found but "GitHub" word exists, mark it for later handling
#     if not github and any("github" in line.lower() for line in lines):
#         github = "GitHub mentioned without URL"
    
#     # Extract portfolio or personal website URL
#     # First look for "portfolio" or "website" mentions and get the nearby URL
#     portfolio = ""
#     for i, line in enumerate(lines):
#         if re.search(r'\b(portfolio|website|personal site|blog)\b', line, re.IGNORECASE):
#             # Check this line and adjacent lines for URLs
#             for j in range(max(0, i-1), min(len(lines), i+2)):
#                 url_match = re.search(portfolio_pattern, lines[j])
#                 if url_match and not re.search(r'(linkedin|github)', url_match.group(0), re.IGNORECASE):
#                     portfolio = url_match.group(0)
#                     break
#             if portfolio:
#                 break
    
#     # If no portfolio found yet, look for any URLs that aren't linkedin or github
#     if not portfolio:
#         for line in lines:
#             url_match = re.search(portfolio_pattern, line)
#             if url_match and not re.search(r'(linkedin|github)', url_match.group(0), re.IGNORECASE):
#                 portfolio = url_match.group(0)
#                 break
    
#     location = next((re.search(location_pattern, line).group(0) for line in lines if re.search(location_pattern, line)), "")
    
#     # Define section headers for detection
#     section_patterns = {
#         'education': r'\b(EDUCATION|Education|Academic Background)\b',
#         'experience': r'\b(EXPERIENCE|Experience|WORK EXPERIENCE|Work Experience|Employment History)\b',
#         'skills': r'\b(SKILLS|Skills|TECHNICAL SKILLS|Technical Skills|TECHNOLOGIES)\b',
#         'projects': r'\b(PROJECTS|Projects|ACADEMIC PROJECTS|Academic Projects)\b'
#     }
    
#     # Find sections in the resume
#     section_indices = {}
#     for i, line in enumerate(lines):
#         for section, pattern in section_patterns.items():
#             if re.search(pattern, line):
#                 section_indices[section] = i
                
#     # Handle cases where sections might be detected through content
#     if 'projects' not in section_indices:
#         # Check if there's a line that likely indicates a projects section
#         for i, line in enumerate(lines):
#             if re.search(r'\b(Web Scraping|App Development|Data Analysis|Analytics Tool|Software Project)\b', line) and \
#                re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b', line):
#                 # This might be a project entry
#                 # Look back a few lines to find a potential section header
#                 for j in range(max(0, i-3), i):
#                     if re.search(r'\b(PROJECTS|Projects|ACADEMIC PROJECTS|Academic Projects)\b', lines[j]):
#                         section_indices['projects'] = j
#                         break
#                 if 'projects' not in section_indices:
#                     # If we couldn't find a header, consider this line the start of projects
#                     section_indices['projects'] = max(0, i-1)

#     # Sort sections by their appearance in the document
#     sorted_sections = sorted(section_indices.items(), key=lambda x: x[1])
    
#     # Extract content for each section
#     sections_content = {}
#     for i, (section, idx) in enumerate(sorted_sections):
#         # Determine the end index of this section (start of next section or end of document)
#         end_idx = sorted_sections[i+1][1] if i+1 < len(sorted_sections) else len(lines)
#         # Get the content (skip the section header)
#         sections_content[section] = lines[idx+1:end_idx]
    
#     # Process education section
#     education_entries = []
#     if 'education' in sections_content:
#         current_university = None
#         current_degree = None
#         current_dates = None
#         current_details = []
        
#         for line in sections_content['education']:
#             # Check if this is a university line
#             if re.search(r'\b(University|College|School|Institute)\b', line, re.IGNORECASE):
#                 # Save previous entry if exists
#                 if current_university:
#                     education_entries.append({
#                         "institution": current_university,
#                         "degree": current_degree,
#                         "dates": current_dates,
#                         "details": current_details
#                     })
                
#                 # Start new entry
#                 current_university = line
#                 current_degree = None
#                 current_dates = None
#                 current_details = []
#             elif current_university:
#                 # Check for degree information
#                 if re.search(r'\b(Bachelor|Master|PhD|Degree|BS|MS|BA|MBA)\b', line, re.IGNORECASE):
#                     current_degree = line
#                 # Check for dates
#                 elif re.search(r'\b(20\d{2}|19\d{2})\b', line):
#                     current_dates = line
#                 # Otherwise, it's additional details
#                 else:
#                     current_details.append(line)
        
#         # Add the last entry
#         if current_university:
#             education_entries.append({
#                 "institution": current_university,
#                 "degree": current_degree,
#                 "dates": current_dates,
#                 "details": current_details
#             })
    
#     # Process experience section
#     experience_entries = []
#     if 'experience' in sections_content:
#         current_company = None
#         current_position = None
#         current_location = None
#         current_dates = None
#         current_responsibilities = []
#         current_company_url = None
        
#         for line in sections_content['experience']:
#             # Check for URLs in the line 
#             url_match = re.search(portfolio_pattern, line)
#             company_url = url_match.group(0) if url_match else None
            
#             # Check if this is a company line (typically contains location)
#             if (not line.startswith('•') and 
#                 (re.search(r'\b(Inc|LLC|Ltd|Corp|Company|Mumbai|Boston|New York|INDIA|USA)\b', line, re.IGNORECASE) or
#                  re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', line))):  # Look for proper nouns
                
#                 # Save previous entry if exists
#                 if current_company:
#                     experience_entries.append({
#                         "company": current_company,
#                         "position": current_position,
#                         "location": current_location,
#                         "dates": current_dates,
#                         "responsibilities": current_responsibilities,
#                         "company_url": current_company_url
#                     })
                
#                 # Start new entry
#                 current_company = line
#                 current_position = None
#                 current_location = None
#                 current_dates = None
#                 current_responsibilities = []
#                 current_company_url = company_url
                
#                 # Try to extract location from company line
#                 location_match = re.search(r'\b([A-Za-z\s]+,\s*[A-Z]{2}|[A-Za-z\s]+,\s*[A-Za-z]+)\b', line)
#                 if location_match:
#                     current_location = location_match.group(0)
                
#             # Check if this is a position line (often contains dates)
#             elif current_company and not line.startswith('•') and re.search(r'\b(Engineer|Developer|Manager|Analyst|Director)\b', line, re.IGNORECASE):
#                 current_position = line
                
#                 # Save URL if found
#                 if company_url and not current_company_url:
#                     current_company_url = company_url
                
#                 # Try to extract dates from position line
#                 date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\b', line)
#                 if date_match:
#                     current_dates = date_match.group(0)
                    
#             # Check if this is a bullet point (responsibility)
#             elif current_company and line.startswith('•'):
#                 # Also check for URLs in responsibilities
#                 bullet_text = line.replace('•', '').strip()
#                 current_responsibilities.append(bullet_text)
                
#                 # Save any URLs found in bullet points
#                 if company_url and not current_company_url:
#                     current_company_url = company_url
                
#             # If we have a company but no position yet, this might be the position line
#             elif current_company and not current_position:
#                 current_position = line
                
#                 # Save URL if found
#                 if company_url and not current_company_url:
#                     current_company_url = company_url
                
#                 # Try to extract dates
#                 date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\b', line)
#                 if date_match:
#                     current_dates = date_match.group(0)
        
#         # Add the last entry
#         if current_company:
#             experience_entries.append({
#                 "company": current_company,
#                 "position": current_position,
#                 "location": current_location,
#                 "dates": current_dates,
#                 "responsibilities": current_responsibilities,
#                 "company_url": current_company_url
#             })
    
#     # Process skills section
#     skills = []
#     if 'skills' in sections_content:
#         for line in sections_content['skills']:
#             # Check for bullet points (• or - or *)
#             if line.startswith('•') or line.startswith('-') or line.startswith('*'):
#                 # Clean up the bullet point and add to skills
#                 skill_text = line.lstrip('•-* ').strip()
#                 skills.append(skill_text)
#             # Handle lines without bullet points but with colon (likely categories)
#             elif ':' in line:
#                 skills.append(line.strip())
#             # Handle lines without bullets or colons (might be a skill category header)
#             elif line.strip() and len(line.strip()) > 2:
#                 skills.append(line.strip())
    
#     # Process projects section
#     project_entries = []
#     if 'projects' in sections_content:
#         current_project = None
#         current_date = None
#         current_description = []
#         current_project_url = None
        
#         for line in sections_content['projects']:
#             # Check for URLs in the line
#             url_match = re.search(portfolio_pattern, line)
#             project_url = url_match.group(0) if url_match else None
            
#             # Check if this is a project title line (typically includes a date)
#             if (not line.startswith('•') and not line.startswith('-') and not line.startswith('*') and 
#                 re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\b', line, re.IGNORECASE)):
#                 # Save previous project if exists
#                 if current_project:
#                     project_entries.append({
#                         "title": current_project,
#                         "date": current_date,
#                         "description": current_description,
#                         "project_url": current_project_url
#                     })
                
#                 # Extract date
#                 date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\b', line, re.IGNORECASE)
#                 if date_match:
#                     current_date = date_match.group(0)
#                     # Remove date from title
#                     current_project = line.replace(date_match.group(0), '').strip()
#                 else:
#                     current_project = line
#                     current_date = ""
                
#                 current_description = []
#                 current_project_url = project_url
            
#             # Check if this is a bullet point for project description
#             elif current_project and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
#                 bullet_text = line.lstrip('•-* ').strip()
#                 current_description.append(bullet_text)
                
#                 # Check for URLs in bullet points
#                 if project_url and not current_project_url:
#                     current_project_url = project_url
                
#             # Check if this is a GitHub link or other project URL
#             elif current_project and (re.search(github_pattern, line) or re.search(portfolio_pattern, line)):
#                 url_match = re.search(portfolio_pattern, line)
#                 if url_match and not current_project_url:
#                     current_project_url = url_match.group(0)
        
#         # Add the last project
#         if current_project:
#             project_entries.append({
#                 "title": current_project,
#                 "date": current_date,
#                 "description": current_description,
#                 "project_url": current_project_url
#             })
    
#     # If no projects were found but there are likely project entries in the text (fallback method)
#     if not project_entries:
#         # Try to find project entries with a different approach
#         project_pattern = r'([A-Za-z\s&]+)(\s+)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+)(\d{4})'
#         project_matches = re.finditer(project_pattern, text)
        
#         for match in project_matches:
#             project_title = match.group(1).strip()
#             project_date = f"{match.group(3)} {match.group(5)}"
            
#             # Find bullet points following this project
#             start_pos = match.end()
#             end_pos = text.find("Jan", start_pos + 1)
#             if end_pos == -1:
#                 end_pos = len(text)
                
#             project_content = text[start_pos:end_pos]
#             description = []
            
#             # Extract bullet points and check for URLs
#             project_url = None
#             for line in project_content.split('\n'):
#                 line = line.strip()
#                 if line.startswith('•') or line.startswith('-') or line.startswith('*'):
#                     description.append(line.lstrip('•-* ').strip())
                
#                 # Check for URLs
#                 url_match = re.search(portfolio_pattern, line)
#                 if url_match and not project_url:
#                     project_url = url_match.group(0)
            
#             if project_title and description:
#                 project_entries.append({
#                     "title": project_title,
#                     "date": project_date,
#                     "description": description,
#                     "project_url": project_url
#                 })

    
#     # Compile the result
#     result = {
#         "name": name,
#         "contact": {
#             "email": email,
#             "phone": phone,
#             "linkedin": linkedin,
#             "github": github,
#             "portfolio": portfolio,
#             "location": location
#         },
#         "education": education_entries,
#         "experience": experience_entries,
#         "skills": skills,
#         "projects": project_entries,
#         "raw_text": text
#     }
    
#     # Generate improved markdown
#     markdown = f"# {name}\n\n"
    
#     # Contact section
#     contact_items = []
#     if phone: contact_items.append(f"📱 {phone}")
#     if email: contact_items.append(f"📧 [{email}](mailto:{email})")
#     if location: contact_items.append(f"📍 {location}")
    
#     # Add LinkedIn with proper link
#     if linkedin:
#         if linkedin.startswith(("http://", "https://", "www.")):
#             # Format the URL properly
#             if not linkedin.startswith(("http://", "https://")):
#                 linkedin_url = "https://" + linkedin
#             else:
#                 linkedin_url = linkedin
#             contact_items.append(f"🔗 [LinkedIn]({linkedin_url})")
#         elif linkedin != "LinkedIn mentioned without URL":
#             contact_items.append(f"🔗 LinkedIn")
    
#     # Add GitHub with proper link
#     if github:
#         if github.startswith(("http://", "https://", "www.")):
#             # Format the URL properly
#             if not github.startswith(("http://", "https://")):
#                 github_url = "https://" + github
#             else:
#                 github_url = github
#             contact_items.append(f"💻 [GitHub]({github_url})")
#         elif github != "GitHub mentioned without URL":
#             contact_items.append(f"💻 GitHub")
    
#     # Add portfolio/personal website with proper link
#     if portfolio:
#         if portfolio.startswith(("http://", "https://", "www.")):
#             # Format the URL properly
#             if not portfolio.startswith(("http://", "https://")):
#                 portfolio_url = "https://" + portfolio
#             else:
#                 portfolio_url = portfolio
#             contact_items.append(f"🌐 [Portfolio]({portfolio_url})")
    
#     markdown += f"**Contact:** {' | '.join(contact_items)}\n\n"
    
#     # Education section
#     if education_entries:
#         markdown += "## 🎓 Education\n\n"
#         for edu in education_entries:
#             markdown += f"### {edu['institution']}\n"
#             if edu.get('degree'):
#                 markdown += f"**{edu['degree']}**\n"
#             if edu.get('dates'):
#                 markdown += f"*{edu['dates']}*\n"
#             for detail in edu.get('details', []):
#                 markdown += f"- {detail}\n"
#             markdown += "\n"
    
#     # Experience section
#     if experience_entries:
#         markdown += "## 💼 Experience\n\n"
#         for exp in experience_entries:
#             # Add company name with URL if available
#             if exp.get('company_url'):
#                 url = exp['company_url']
#                 if not url.startswith(("http://", "https://")):
#                     url = "https://" + url
#                 markdown += f"### [{exp['company']}]({url})\n"
#             else:
#                 markdown += f"### {exp['company']}\n"
            
#             if exp.get('position'):
#                 markdown += f"**{exp['position']}**\n"
            
#             location_date = []
#             if exp.get('location'): location_date.append(exp['location'])
#             if exp.get('dates'): location_date.append(exp['dates'])
            
#             if location_date:
#                 markdown += f"*{' | '.join(location_date)}*\n\n"
            
#             for resp in exp.get('responsibilities', []):
#                 # Check if the responsibility contains a URL and format it as a link
#                 url_match = re.search(portfolio_pattern, resp)
#                 if url_match:
#                     url = url_match.group(0)
#                     # Format the URL properly
#                     if not url.startswith(("http://", "https://")):
#                         formatted_url = "https://" + url
#                     else:
#                         formatted_url = url
#                     # Replace the raw URL with a formatted Markdown link
#                     resp = resp.replace(url, f"[{url}]({formatted_url})")
                
#                 markdown += f"- {resp}\n"
#             markdown += "\n"
    
#     # Skills section
#     if skills:
#         markdown += "## 🔧 Skills\n\n"
        
#         # Group skills by category if they follow "Category: skill1, skill2" pattern
#         current_category = None
        
#         for skill in skills:
#             if ":" in skill:
#                 # This is a category with skills list
#                 category, skill_list = skill.split(":", 1)
#                 markdown += f"**{category.strip()}:** {skill_list.strip()}\n\n"
#                 current_category = category.strip()
#             elif skill.strip() and all(c.isupper() or c.isspace() for c in skill):
#                 # This is likely a category header (all caps)
#                 markdown += f"### {skill}\n"
#                 current_category = skill
#             else:
#                 # This is a regular skill item
#                 markdown += f"- {skill}\n"
    
#     # Projects section
#     if project_entries:
#         markdown += "## 🚀 Projects\n\n"
#         for project in project_entries:
#             # Add project title with URL if available
#             if project.get('project_url'):
#                 url = project['project_url']
#                 if not url.startswith(("http://", "https://")):
#                     url = "https://" + url
                    
#                 # Check if it's a GitHub URL to add appropriate icon
#                 if "github.com" in url.lower():
#                     markdown += f"### 💻 [{project['title']}]({url})"
#                 else:
#                     markdown += f"### [{project['title']}]({url})"
#             else:
#                 markdown += f"### {project['title']}"
                
#             if project.get('date'):
#                 markdown += f" *({project['date']})*"
#             markdown += "\n"
            
#             for detail in project.get('description', []):
#                 # Check if the description contains a URL and format it as a link
#                 url_match = re.search(portfolio_pattern, detail)
#                 if url_match:
#                     url = url_match.group(0)
#                     # Format the URL properly
#                     if not url.startswith(("http://", "https://")):
#                         formatted_url = "https://" + url
#                     else:
#                         formatted_url = url
#                     # Replace the raw URL with a formatted Markdown link
#                     detail = detail.replace(url, f"[{url}]({formatted_url})")
                
#                 markdown += f"- {detail}\n"
#             markdown += "\n"
    
#     return result, markdown

# @app.post("/upload/", response_model=ResumeData)
# async def upload_resume(file: UploadFile = File(...)):
#     """
#     Upload and process a resume file
#     """
#     # Generate a unique ID for the resume
#     resume_id = str(uuid.uuid4())
    
#     # Get file extension
#     file_extension = os.path.splitext(file.filename)[1].lower()
    
#     # Check if the file type is supported
#     if file_extension not in ['.pdf', '.docx', '.txt']:
#         raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, or TXT files.")
    
#     # Save the uploaded file
#     file_path = UPLOAD_DIR / f"{resume_id}{file_extension}"
#     with open(file_path, "wb") as buffer:
#         buffer.write(await file.read())
    
#     # Extract text based on file type
#     if file_extension == '.pdf':
#         text = extract_text_from_pdf(file_path)
#     elif file_extension == '.docx':
#         text = extract_text_from_docx(file_path)
#     else:  # .txt
#         text = extract_text_from_txt(file_path)
    
#     # Parse the resume text
#     parsed_data, markdown = parse_resume(text)
    
#     # Save the parsed resume
#     resume_data = {
#         "resume_id": resume_id,
#         "content": text,
#         "metadata": parsed_data,
#         "markdown": markdown
#     }
    
#     # Save to our in-memory database
#     parsed_resumes[resume_id] = resume_data
    
#     # Save to file for persistence
#     with open(PARSED_DIR / f"{resume_id}.json", "w") as json_file:
#         json.dump(resume_data, json_file)
    
#     return resume_data

# @app.get("/resumes/", response_model=ResumeList)
# async def get_all_resumes():
#     """
#     Get a list of all parsed resumes
#     """
#     return {"resumes": list(parsed_resumes.values())}

# @app.get("/resume/{resume_id}", response_model=ResumeData)
# async def get_resume(resume_id: str):
#     """
#     Get a specific parsed resume by ID
#     """
#     if resume_id not in parsed_resumes:
#         # Try to load from file
#         resume_path = PARSED_DIR / f"{resume_id}.json"
#         if resume_path.exists():
#             with open(resume_path, "r") as json_file:
#                 parsed_resumes[resume_id] = json.load(json_file)
#         else:
#             raise HTTPException(status_code=404, detail="Resume not found")
    
#     return parsed_resumes[resume_id]

# if __name__ == "__main__":
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)




import os
import uuid
import re
from typing import Dict, List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import PyPDF2
import docx2txt
import json
from pathlib import Path
import markdown2

# Create necessary directories
UPLOAD_DIR = Path("uploads")
PARSED_DIR = Path("parsed_resumes")
STATIC_DIR = Path("static")
TEMPLATES_DIR = Path("templates")

for directory in [UPLOAD_DIR, PARSED_DIR, STATIC_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)

# Create basic CSS file for styling
with open(STATIC_DIR / "styles.css", "w") as css_file:
    css_file.write("""
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 0;
        padding: 20px;
        color: #333;
    }
    .resume-container {
        max-width: 900px;
        margin: 0 auto;
        border: 1px solid #ddd;
        padding: 30px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .resume-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .contact-info {
        text-align: center;
        margin-bottom: 30px;
    }
    .section {
        margin-bottom: 30px;
    }
    h1 {
        color: #2c3e50;
        margin-bottom: 10px;
    }
    h2 {
        color: #3498db;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
        margin-top: 25px;
    }
    h3 {
        color: #2c3e50;
        margin-bottom: 5px;
    }
    ul {
        padding-left: 20px;
    }
    .tabs {
        display: flex;
        margin-bottom: 20px;
        border-bottom: 1px solid #ddd;
    }
    .tab {
        padding: 10px 20px;
        cursor: pointer;
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-bottom: none;
        margin-right: 5px;
    }
    .tab.active {
        background: white;
        border-bottom: 1px solid white;
    }
    .tab-content {
        display: none;
    }
    .tab-content.active {
        display: block;
    }
    pre {
        background: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    a {
        color: #3498db;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    .contact-item {
        display: inline-block;
        margin: 0 10px;
    }
    """)

# Create template for displaying resume
with open(TEMPLATES_DIR / "resume.html", "w") as html_file:
    html_file.write("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ resume.metadata.name }} | Resume</title>
        <link rel="stylesheet" href="/static/styles.css">
        <script>
            function switchTab(tabName) {
                // Hide all tab contents
                const tabContents = document.querySelectorAll('.tab-content');
                tabContents.forEach(content => {
                    content.classList.remove('active');
                });
                
                // Deactivate all tabs
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Activate the selected tab and its content
                document.getElementById(tabName).classList.add('active');
                document.getElementById(tabName + '-content').classList.add('active');
            }
            
            document.addEventListener('DOMContentLoaded', function() {
                // Initialize the first tab as active
                switchTab('markdown');
            });
        </script>
    </head>
    <body>
        <div class="resume-container">
            <h1>Resume Viewer: {{ resume.metadata.name }}</h1>
            
            <div class="tabs">
                <div id="markdown" class="tab active" onclick="switchTab('markdown')">Formatted Resume</div>
                <div id="json" class="tab" onclick="switchTab('json')">Structured Data</div>
                <div id="raw" class="tab" onclick="switchTab('raw')">Raw Text</div>
            </div>
            
            <div id="markdown-content" class="tab-content active">
                {{ markdown_content|safe }}
            </div>
            
            <div id="json-content" class="tab-content">
                <pre>{{ json_content }}</pre>
            </div>
            
            <div id="raw-content" class="tab-content">
                <pre>{{ resume.content }}</pre>
            </div>
        </div>
    </body>
    </html>
    """)

# Create template for the home page/upload form
with open(TEMPLATES_DIR / "index.html", "w") as html_file:
    html_file.write("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume Parser</title>
        <link rel="stylesheet" href="/static/styles.css">
        <style>
            .upload-container {
                max-width: 600px;
                margin: 50px auto;
                padding: 30px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                text-align: center;
            }
            .upload-form {
                margin: 20px 0;
            }
            .btn {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            .btn:hover {
                background-color: #2980b9;
            }
            .resume-list {
                margin-top: 30px;
                text-align: left;
            }
            .resume-item {
                margin-bottom: 10px;
                padding: 10px;
                border: 1px solid #eee;
                border-radius: 4px;
            }
            .resume-item:hover {
                background-color: #f5f5f5;
            }
        </style>
    </head>
    <body>
        <div class="upload-container">
            <h1>Resume Parser</h1>
            <p>Upload a resume (PDF, DOCX, or TXT) to parse and analyze it.</p>
            
            <div class="upload-form">
                <form action="/upload/" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".pdf,.docx,.txt" required>
                    <button type="submit" class="btn">Upload & Parse</button>
                </form>
            </div>
            
            <div class="resume-list">
                <h2>Previously Parsed Resumes</h2>
                {% if resumes %}
                    <ul>
                        {% for resume in resumes %}
                            <li class="resume-item">
                                <a href="/view/{{ resume.resume_id }}">{{ resume.metadata.name }}</a>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p>No resumes have been parsed yet.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """)

app = FastAPI(title="Resume Parser API")

# Add CORS middleware to allow Streamlit to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

class ResumeData(BaseModel):
    resume_id: str
    content: str
    metadata: Dict
    markdown: str

class ResumeList(BaseModel):
    resumes: List[Dict]

# In-memory database (for demo purposes - in production, use a real DB)
parsed_resumes = {}

def extract_text_from_pdf(file_path):
    """Extract text from PDF files"""
    text = ""
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX files"""
    return docx2txt.process(file_path)

def extract_text_from_txt(file_path):
    """Extract text from TXT files"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as txt_file:
        return txt_file.read()

def parse_resume(text):
    """
    Advanced resume parser that identifies sections and extracts structured information
    including links for LinkedIn, GitHub, and other URLs
    """
    # Clean and prepare the text
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Extract name (typically the first line of the resume)
    name = lines[0] if lines else ""
    
    # Extract contact information using regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    
    # Enhanced patterns for social and professional links
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+'
    portfolio_pattern = r'(?:https?://)?(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}(?:/[^\s]*)?'
    location_pattern = r'[A-Za-z]+\s*,\s*[A-Z]{2}'  # City, State format
    
    email = next((re.search(email_pattern, line).group(0) for line in lines if re.search(email_pattern, line)), "")
    phone = next((re.search(phone_pattern, line).group(0) for line in lines if re.search(phone_pattern, line)), "")
    
    # Extract LinkedIn URL
    linkedin = next((re.search(linkedin_pattern, line).group(0) for line in lines if re.search(linkedin_pattern, line)), "")
    # If no LinkedIn URL found but "LinkedIn" word exists, mark it for later handling
    if not linkedin and any("linkedin" in line.lower() for line in lines):
        linkedin = "LinkedIn mentioned without URL"
    
    # Extract GitHub URL
    github = next((re.search(github_pattern, line).group(0) for line in lines if re.search(github_pattern, line)), "")
    # If no GitHub URL found but "GitHub" word exists, mark it for later handling
    if not github and any("github" in line.lower() for line in lines):
        github = "GitHub mentioned without URL"
    
    # Extract portfolio or personal website URL
    # First look for "portfolio" or "website" mentions and get the nearby URL
    portfolio = ""
    for i, line in enumerate(lines):
        if re.search(r'\b(portfolio|website|personal site|blog)\b', line, re.IGNORECASE):
            # Check this line and adjacent lines for URLs
            for j in range(max(0, i-1), min(len(lines), i+2)):
                url_match = re.search(portfolio_pattern, lines[j])
                if url_match and not re.search(r'(linkedin|github)', url_match.group(0), re.IGNORECASE):
                    portfolio = url_match.group(0)
                    break
            if portfolio:
                break
    
    # If no portfolio found yet, look for any URLs that aren't linkedin or github
    if not portfolio:
        for line in lines:
            url_match = re.search(portfolio_pattern, line)
            if url_match and not re.search(r'(linkedin|github)', url_match.group(0), re.IGNORECASE):
                portfolio = url_match.group(0)
                break
    
    location = next((re.search(location_pattern, line).group(0) for line in lines if re.search(location_pattern, line)), "")
    
    # Define section headers for detection
    section_patterns = {
        'education': r'\b(EDUCATION|Education|Academic Background)\b',
        'experience': r'\b(EXPERIENCE|Experience|WORK EXPERIENCE|Work Experience|Employment History)\b',
        'skills': r'\b(SKILLS|Skills|TECHNICAL SKILLS|Technical Skills|TECHNOLOGIES)\b',
        'projects': r'\b(PROJECTS|Projects|ACADEMIC PROJECTS|Academic Projects)\b'
    }
    
    # Find sections in the resume
    section_indices = {}
    for i, line in enumerate(lines):
        for section, pattern in section_patterns.items():
            if re.search(pattern, line):
                section_indices[section] = i
                
    # Handle cases where sections might be detected through content
    if 'projects' not in section_indices:
        # Check if there's a line that likely indicates a projects section
        for i, line in enumerate(lines):
            if re.search(r'\b(Web Scraping|App Development|Data Analysis|Analytics Tool|Software Project)\b', line) and \
               re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b', line):
                # This might be a project entry
                # Look back a few lines to find a potential section header
                for j in range(max(0, i-3), i):
                    if re.search(r'\b(PROJECTS|Projects|ACADEMIC PROJECTS|Academic Projects)\b', lines[j]):
                        section_indices['projects'] = j
                        break
                if 'projects' not in section_indices:
                    # If we couldn't find a header, consider this line the start of projects
                    section_indices['projects'] = max(0, i-1)

    # Sort sections by their appearance in the document
    sorted_sections = sorted(section_indices.items(), key=lambda x: x[1])
    
    # Extract content for each section
    sections_content = {}
    for i, (section, idx) in enumerate(sorted_sections):
        # Determine the end index of this section (start of next section or end of document)
        end_idx = sorted_sections[i+1][1] if i+1 < len(sorted_sections) else len(lines)
        # Get the content (skip the section header)
        sections_content[section] = lines[idx+1:end_idx]
    
    # Process education section
    education_entries = []
    if 'education' in sections_content:
        current_university = None
        current_degree = None
        current_dates = None
        current_details = []
        
        for line in sections_content['education']:
            # Check if this is a university line
            if re.search(r'\b(University|College|School|Institute)\b', line, re.IGNORECASE):
                # Save previous entry if exists
                if current_university:
                    education_entries.append({
                        "institution": current_university,
                        "degree": current_degree,
                        "dates": current_dates,
                        "details": current_details
                    })
                
                # Start new entry
                current_university = line
                current_degree = None
                current_dates = None
                current_details = []
            elif current_university:
                # Check for degree information
                if re.search(r'\b(Bachelor|Master|PhD|Degree|BS|MS|BA|MBA)\b', line, re.IGNORECASE):
                    current_degree = line
                # Check for dates
                elif re.search(r'\b(20\d{2}|19\d{2})\b', line):
                    current_dates = line
                # Otherwise, it's additional details
                else:
                    current_details.append(line)
        
        # Add the last entry
        if current_university:
            education_entries.append({
                "institution": current_university,
                "degree": current_degree,
                "dates": current_dates,
                "details": current_details
            })
    
    # Process experience section
    experience_entries = []
    if 'experience' in sections_content:
        current_company = None
        current_position = None
        current_location = None
        current_dates = None
        current_responsibilities = []
        current_company_url = None
        
        for line in sections_content['experience']:
            # Check for URLs in the line 
            url_match = re.search(portfolio_pattern, line)
            company_url = url_match.group(0) if url_match else None
            
            # Check if this is a company line (typically contains location)
            if (not line.startswith('•') and 
                (re.search(r'\b(Inc|LLC|Ltd|Corp|Company|Mumbai|Boston|New York|INDIA|USA)\b', line, re.IGNORECASE) or
                 re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', line))):  # Look for proper nouns
                
                # Save previous entry if exists
                if current_company:
                    experience_entries.append({
                        "company": current_company,
                        "position": current_position,
                        "location": current_location,
                        "dates": current_dates,
                        "responsibilities": current_responsibilities,
                        "company_url": current_company_url
                    })
                
                # Start new entry
                current_company = line
                current_position = None
                current_location = None
                current_dates = None
                current_responsibilities = []
                current_company_url = company_url
                
                # Try to extract location from company line
                location_match = re.search(r'\b([A-Za-z\s]+,\s*[A-Z]{2}|[A-Za-z\s]+,\s*[A-Za-z]+)\b', line)
                if location_match:
                    current_location = location_match.group(0)
                
            # Check if this is a position line (often contains dates)
            elif current_company and not line.startswith('•') and re.search(r'\b(Engineer|Developer|Manager|Analyst|Director)\b', line, re.IGNORECASE):
                current_position = line
                
                # Save URL if found
                if company_url and not current_company_url:
                    current_company_url = company_url
                
                # Try to extract dates from position line
                date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\b', line)
                if date_match:
                    current_dates = date_match.group(0)
                    
            # Check if this is a bullet point (responsibility)
            elif current_company and line.startswith('•'):
                # Also check for URLs in responsibilities
                bullet_text = line.replace('•', '').strip()
                current_responsibilities.append(bullet_text)
                
                # Save any URLs found in bullet points
                if company_url and not current_company_url:
                    current_company_url = company_url
                
            # If we have a company but no position yet, this might be the position line
            elif current_company and not current_position:
                current_position = line
                
                # Save URL if found
                if company_url and not current_company_url:
                    current_company_url = company_url
                
                # Try to extract dates
                date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\b', line)
                if date_match:
                    current_dates = date_match.group(0)
        
        # Add the last entry
        if current_company:
            experience_entries.append({
                "company": current_company,
                "position": current_position,
                "location": current_location,
                "dates": current_dates,
                "responsibilities": current_responsibilities,
                "company_url": current_company_url
            })
    
    # Process skills section
    skills = []
    if 'skills' in sections_content:
        for line in sections_content['skills']:
            # Check for bullet points (• or - or *)
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Clean up the bullet point and add to skills
                skill_text = line.lstrip('•-* ').strip()
                skills.append(skill_text)
            # Handle lines without bullet points but with colon (likely categories)
            elif ':' in line:
                skills.append(line.strip())
            # Handle lines without bullets or colons (might be a skill category header)
            elif line.strip() and len(line.strip()) > 2:
                skills.append(line.strip())
    
    # Process projects section
    project_entries = []
    if 'projects' in sections_content:
        current_project = None
        current_date = None
        current_description = []
        current_project_url = None
        
        for line in sections_content['projects']:
            # Check for URLs in the line
            url_match = re.search(portfolio_pattern, line)
            project_url = url_match.group(0) if url_match else None
            
            # Check if this is a project title line (typically includes a date)
            if (not line.startswith('•') and not line.startswith('-') and not line.startswith('*') and 
                re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\b', line, re.IGNORECASE)):
                # Save previous project if exists
                if current_project:
                    project_entries.append({
                        "title": current_project,
                        "date": current_date,
                        "description": current_description,
                        "project_url": current_project_url
                    })
                
                # Extract date
                date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\b', line, re.IGNORECASE)
                if date_match:
                    current_date = date_match.group(0)
                    # Remove date from title
                    current_project = line.replace(date_match.group(0), '').strip()
                else:
                    current_project = line
                    current_date = ""
                
                current_description = []
                current_project_url = project_url
            
            # Check if this is a bullet point for project description
            elif current_project and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                bullet_text = line.lstrip('•-* ').strip()
                current_description.append(bullet_text)
                
                # Check for URLs in bullet points
                if project_url and not current_project_url:
                    current_project_url = project_url
                
            # Check if this is a GitHub link or other project URL
            elif current_project and (re.search(github_pattern, line) or re.search(portfolio_pattern, line)):
                url_match = re.search(portfolio_pattern, line)
                if url_match and not current_project_url:
                    current_project_url = url_match.group(0)
        
        # Add the last project
        if current_project:
            project_entries.append({
                "title": current_project,
                "date": current_date,
                "description": current_description,
                "project_url": current_project_url
            })
    
    # If no projects were found but there are likely project entries in the text (fallback method)
    if not project_entries:
        # Try to find project entries with a different approach
        project_pattern = r'([A-Za-z\s&]+)(\s+)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+)(\d{4})'
        project_matches = re.finditer(project_pattern, text)
        
        for match in project_matches:
            project_title = match.group(1).strip()
            project_date = f"{match.group(3)} {match.group(5)}"
            
            # Find bullet points following this project
            start_pos = match.end()
            end_pos = text.find("Jan", start_pos + 1)
            if end_pos == -1:
                end_pos = len(text)
                
            project_content = text[start_pos:end_pos]
            description = []
            
            # Extract bullet points and check for URLs
            project_url = None
            for line in project_content.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    description.append(line.lstrip('•-* ').strip())
                
                # Check for URLs
                url_match = re.search(portfolio_pattern, line)
                if url_match and not project_url:
                    project_url = url_match.group(0)
            
            if project_title and description:
                project_entries.append({
                    "title": project_title,
                    "date": project_date,
                    "description": description,
                    "project_url": project_url
                })

    
    # Compile the result
    result = {
        "name": name,
        "contact": {
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
            "location": location
        },
        "education": education_entries,
        "experience": experience_entries,
        "skills": skills,
        "projects": project_entries
    }
    
    # Generate improved markdown
    markdown = f"# {name}\n\n"
    
    # Contact section
    contact_items = []
    if phone: contact_items.append(f"📱 {phone}")
    if email: contact_items.append(f"📧 [{email}](mailto:{email})")
    if location: contact_items.append(f"📍 {location}")
    
    # Add LinkedIn with proper link
    if linkedin:
        if linkedin.startswith(("http://", "https://", "www.")):
            # Format the URL properly
            if not linkedin.startswith(("http://", "https://")):
                linkedin_url = "https://" + linkedin
            else:
                linkedin_url = linkedin
            contact_items.append(f"🔗 [LinkedIn]({linkedin_url})")
        elif linkedin != "LinkedIn mentioned without URL":
            contact_items.append(f"🔗 LinkedIn")
    
    # Add GitHub with proper link
    if github:
        if github.startswith(("http://", "https://", "www.")):
            # Format the URL properly
            if not github.startswith(("http://", "https://")):
                github_url = "https://" + github
            else:
                github_url = github
            contact_items.append(f"💻 [GitHub]({github_url})")
        elif github != "GitHub mentioned without URL":
            contact_items.append(f"💻 GitHub")
    
    # Add portfolio/personal website with proper link
    if portfolio:
        if portfolio.startswith(("http://", "https://", "www.")):
            # Format the URL properly
            if not portfolio.startswith(("http://", "https://")):
                portfolio_url = "https://" + portfolio
            else:
                portfolio_url = portfolio
            contact_items.append(f"🌐 [Portfolio]({portfolio_url})")
    
    markdown += f"**Contact:** {' | '.join(contact_items)}\n\n"
    
    # Education section
    if education_entries:
        markdown += "## 🎓 Education\n\n"
        for edu in education_entries:
            markdown += f"### {edu['institution']}\n"
            if edu.get('degree'):
                markdown += f"**{edu['degree']}**\n"
            if edu.get('dates'):
                markdown += f"*{edu['dates']}*\n"
            for detail in edu.get('details', []):
                markdown += f"- {detail}\n"
            markdown += "\n"
    
    # Experience section
    if experience_entries:
        markdown += "## 💼 Experience\n\n"
        for exp in experience_entries:
            # Add company name with URL if available
            if exp.get('company_url'):
                url = exp['company_url']
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                markdown += f"### [{exp['company']}]({url})\n"
            else:
                markdown += f"### {exp['company']}\n"
            
            if exp.get('position'):
                markdown += f"**{exp['position']}**\n"
            
            location_date = []
            if exp.get('location'): location_date.append(exp['location'])
            if exp.get('dates'): location_date.append(exp['dates'])
            
            if location_date:
                markdown += f"*{' | '.join(location_date)}*\n\n"
            
            for resp in exp.get('responsibilities', []):
                # Check if the responsibility contains a URL and format it as a link
                url_match = re.search(portfolio_pattern, resp)
                if url_match:
                    url = url_match.group(0)
                    # Format the URL properly
                    if not url.startswith(("http://", "https://")):
                        formatted_url = "https://" + url
                    else:
                        formatted_url = url
                    # Replace the raw URL with a formatted Markdown link
                    resp = resp.replace(url, f"[{url}]({formatted_url})")
                
                markdown += f"- {resp}\n"
            markdown += "\n"
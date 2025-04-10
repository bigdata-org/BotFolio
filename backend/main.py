from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

# env = Environment(loader=FileSystemLoader("templates"))

# app.mount("/static", StaticFiles(directory="static"), name="static")



template_folder = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(template_folder)))

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


print(template_folder)



genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def enhance_text_with_gemini(description: str) -> str:
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Polish this resume experience to sound professional:\n{description}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini failed:", e)
        return description 

def enhance_resume(parsed_resume: dict) -> dict:
    for exp in parsed_resume.get("experience", []):
        exp["description"] = enhance_text_with_gemini(exp["description"])
    return parsed_resume


def generate_portfolio_content(parsed_resume: dict, theme: str) -> str:
    template = env.get_template(f"{theme}.html")
    return template.render(profile=parsed_resume)

@app.post("/generate_portfolio/")
async def generate_portfolio(resume_json: UploadFile, theme: str = Form(...), username: str = Form(...)):
    content = await resume_json.read()
    parsed_resume = json.loads(content.decode())

   
    enhanced_resume = enhance_resume(parsed_resume)

    html_content = generate_portfolio_content(enhanced_resume, theme)

    user_dir = Path(f"./output/{username}")
    user_dir.mkdir(parents=True, exist_ok=True)

    with open(user_dir / "index.html", "w") as f:
        f.write(html_content)

    return JSONResponse(content={"message": "Portfolio generated!", "path": f"/output/{username}/index.html"})


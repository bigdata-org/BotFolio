
import json
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import streamlit as st

template_folder = Path(__file__).parent / "templates"  
env = Environment(loader=FileSystemLoader(str(template_folder)))

uploaded_file = st.file_uploader("Upload your resume JSON", type="json")
if uploaded_file is not None:
    try:
        resume = json.load(uploaded_file)

        
        template = env.get_template("theme3.html")

       
        rendered_html = template.render(resume=resume)

        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "index.html"), "w") as f:
            f.write(rendered_html)

        st.success("Portfolio generated successfully! Check the output folder.")
        st.markdown(f"Your portfolio is ready! View it [here](./output/index.html).")

    except json.JSONDecodeError:
        st.error("Error: The uploaded file is not a valid JSON.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

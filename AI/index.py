from google import genai
from google.genai import types
from config import get_settings
from requestModel.index import HiringFacts
from sqlmodel import select, Session
from database.model import Jobs
from database.connection import engine
import json



settings = get_settings()

def insert_data_to_jobs(job_id: int, extracted_json_string: str):
    with Session(engine) as session:
        job_exist = session.exec(select(Jobs).where(Jobs.id == job_id)).first()
        print("job_exist",job_exist)
        if job_exist:
            try:
                data_dict = json.loads(extracted_json_string) 
                   
                job_exist.position_title = job_exist.position_title or data_dict.get("title") or None
                job_exist.salary_min = job_exist.salary_min or data_dict.get("salary_min") or None
                job_exist.salary_max = job_exist.salary_max or data_dict.get("salary_max") or None
                job_exist.headcount = job_exist.headcount or data_dict.get("headcount") or None
            
                job_exist.required_skills = job_exist.required_skills or (json.dumps(data_dict.get("required_skills")) if data_dict.get("required_skills") else None)
                job_exist.languages = job_exist.languages or (json.dumps(data_dict.get("languages")) if data_dict.get("languages") else None)
                job_exist.tech_stacks = job_exist.tech_stacks or (json.dumps(data_dict.get("tech_stacks")) if data_dict.get("tech_stacks") else None)
                job_exist.job_tags = job_exist.job_tags or (json.dumps(data_dict.get("job_tags")) if data_dict.get("job_tags") else None)
            
                job_exist.years_of_experience_max = job_exist.years_of_experience_max or data_dict.get("years_of_experience_max") or None
                job_exist.years_of_experience_min = job_exist.years_of_experience_min or data_dict.get("years_of_experience_min") or None
                job_exist.jd_text = job_exist.jd_text or data_dict.get("jd_text") or None
            
                job_exist.extraction_status = "succeeded"
                job_exist.status = "completed"
                session.add(job_exist)
                session.commit()
                
               
            except Exception as json_err:
                print(f"Error parsing JSON data or saving to DB: {json_err}")
                job_exist.extraction_status = "failed"
                job_exist.extraction_error = json_err
                session.add(job_exist)
                session.commit()
        return None



def run_ai(job_id: int, transcript: str):
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"""
        Extract hiring facts from this meeting transcript.
        Rules:
        - Use only facts a speaker clearly said.
        - If a field was not said, return null.
        - Do not invent skills, salary, years, languages, tech, tags, or headcount.

        Transcript:
        {transcript}
        """

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=HiringFacts,
            ),
        )
        
        extracted_json_string = response.text
        print(f"Extracted JSON for Job {job_id} =", extracted_json_string)
        
        insert_data_to_jobs(job_id, extracted_json_string)

    except Exception as e:
        print(f"AI Extraction failed for Job {job_id}: {e}")
        with Session(engine) as session:
            job_exist = session.exec(select(Jobs).where(Jobs.id == job_id)).first()
            if job_exist:
                job_exist.extraction_status = "failed"
                session.add(job_exist)
                session.commit()
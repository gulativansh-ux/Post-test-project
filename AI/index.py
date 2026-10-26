from google import genai
from google.genai import types
from config import get_settings
from requestModel.index import HiringFacts
from sqlmodel import select, Session
from database.model import Jobs
from database.connection import engine
import json
from database.model import Notification
import anyio
from security.websocket import notification_manager

settings = get_settings()

def insert_data_to_jobs(job_id: int, extracted_json_string: str):
    with Session(engine) as session:
        job_exist = session.exec(select(Jobs).where(Jobs.id == job_id)).first()
        
        if not job_exist:
            return False
        
        if job_exist:
            try:
                data_dict = json.loads(extracted_json_string)

                job_exist.position_title = (
                    job_exist.position_title or data_dict.get("title") or None
                )
                job_exist.salary_min = (
                    job_exist.salary_min or data_dict.get("salary_min") or None
                )
                job_exist.salary_max = (
                    job_exist.salary_max or data_dict.get("salary_max") or None
                )
                job_exist.headcount = (
                    job_exist.headcount or data_dict.get("headcount") or None
                )

                job_exist.required_skills = job_exist.required_skills or (
                    json.dumps(data_dict.get("required_skills"))
                    if data_dict.get("required_skills")
                    else None
                )
                job_exist.languages = job_exist.languages or (
                    json.dumps(data_dict.get("languages"))
                    if data_dict.get("languages")
                    else None
                )
                job_exist.tech_stacks = job_exist.tech_stacks or (
                    json.dumps(data_dict.get("tech_stacks"))
                    if data_dict.get("tech_stacks")
                    else None
                )
                job_exist.job_tags = job_exist.job_tags or (
                    json.dumps(data_dict.get("job_tags"))
                    if data_dict.get("job_tags")
                    else None
                )

                job_exist.years_of_experience_max = (
                    job_exist.years_of_experience_max
                    or data_dict.get("years_of_experience_max")
                    or None
                )
                job_exist.years_of_experience_min = (
                    job_exist.years_of_experience_min
                    or data_dict.get("years_of_experience_min")
                    or None
                )
                job_exist.jd_text = (
                    job_exist.jd_text or data_dict.get("jd_text") or None
                )
                job_exist.extraction_status = "succeeded"
                job_exist.status = "completed"
                session.add(job_exist)
                session.commit()
                return True
            except Exception as json_err:
                print(f"Error parsing JSON data or saving to DB: {json_err}")
                job_exist.extraction_status = "failed"
                job_exist.extraction_error = str(json_err)
                session.add(job_exist)
                session.commit()
                return False


def save_and_push_notification(
    user_id: int,
    job_id: int,
    isSuccess: bool,
    job_name:str
):
    title = "Job extraction completed" if isSuccess else "Job extraction failed"

    message = (
        f"AI extraction for Job {job_name} completed successfully."
        if isSuccess
        else f"AI extraction for Job {job_name} failed."
    )

    try:
        with Session(engine) as session:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                job_id=job_id,
                is_read=False,
            )

            session.add(notification)
            session.commit()
            session.refresh(notification)

            event = {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "job_id": notification.job_id,
                "is_read": notification.is_read,
            }

        anyio.from_thread.run(
            notification_manager.send_to_user,
            user_id,
            event,
        )

    except Exception as exc:
        print(f"Notification error for Job {job_id}: {exc}")


def run_ai(job_id: int, transcript: str, notification_user_id: int):
    is_success = False
    with Session(engine) as session:
                job = session.exec(
                    select(Jobs).where(Jobs.id == job_id)
                ).first()
    
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

        if not response.text:
            raise ValueError("Gemini returned an empty response")

        is_success = insert_data_to_jobs(job_id, response.text)

    except Exception as exc:
        print(f"AI extraction failed for Job {job_id}: {exc}")
        if job:
            job.extraction_status = "failed"
            job.extraction_error = str(exc)
            session.add(job)
            session.commit()
    
    finally:
        save_and_push_notification(
            notification_user_id,
            job_id,
            is_success,
            job.position_title
        )
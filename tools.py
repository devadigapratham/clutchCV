# Define tools
from ast import List
from langchain.agents import tool
from data_loader import load_cv, write_to_docx
from search import job_threads, get_job_ids
import asyncio
from langchain.pydantic_v1 import BaseModel, Field

@tool
def job_pipeline(
    keywords: str,
    location_name: str,
    job_type: str = None,
    limit: int = 10,
    companies: str = None,
    industries: str = None,
    remote: str = None
) -> dict:
    """
    Search LinkedIn for job postings based on specified criteria. Returns detailed job listings.

    Parameters:
    - keywords (str): Keywords describing the job role.
    - location_name (str): Geographic location for the job search.
    - job_type (str, optional): Specific type of job to search for.
    - limit (int, optional): Maximum number of jobs to retrieve.
    - companies (str, optional): Filter jobs by company names.
    - industries (str, optional): Filter jobs by industry types.
    - remote (str, optional): Specify if the jobs should be remote.

    Returns:
    - dict: A dictionary containing job titles, company URLs, job locations, and detailed job descriptions.
    """
    job_ids = get_job_ids(keywords, location_name, job_type, limit, companies, industries, remote)
    print(job_ids)
    job_desc = asyncio.run(job_threads(job_ids))
    return job_desc


@tool("extractor_tool", return_direct=False)
def extract_cv() -> dict:
    """
    Extract and structure job-relevant information from an uploaded CV.

    Returns:
    - dict: The content highlighting skills, experience, and qualifications relevant to job applications, omitting personal information.
    """
    cv_extracted_json = {}
    text = load_cv("tmp/cv.pdf")
    cv_extracted_json['content'] = text
    return cv_extracted_json


@tool
def generate_letter_for_specific_job(cv_details: str, job_details: str) -> str:
    """
    Generate a tailored cover letter using the provided CV and job details.

    Parameters:
    - cv_details (str): Extracted details from the CV.
    - job_details (str): Job requirements and description.

    Returns:
    - str: A personalized cover letter articulating how the applicant's skills and experiences align with the job requirements.

    Prompt for the LLM:
    ```<prompt>
    Based on the CV details provided in {cv_details} and the job requirements listed in {job_details},
    write a personalized cover letter. Ensure the letter articulates how the applicant's skills and experiences align with the job requirements.
    ```
    """
    return {
        'content': f"""Based on the CV details and job requirements provided, 
        here is a professionally crafted cover letter that emphasizes relevant skills and experiences 
        while maintaining a formal tone and structure."""
    }


def get_tools():
    return [job_pipeline, extract_cv, generate_letter_for_specific_job]

@tool 
def func_alternative_tool(msg: str, members):
    """This will act as a Router Tool which will rout ethe message among diff members"""
    members = ["Analyzer", "Generator", "Searcher"]
    options = ["FINISH"] + members 
    # Using openai function calling can make the output parsing easier for us 
    function_def = {
        "name": "route", 
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object", 
            "properties": {
                "next": {
                    "title": "Next", 
                    "anyOf": [
                        {"enum": options},
                    ],
                }
            },
            "required": ["next"], 
        }, 
    }

    return function_def
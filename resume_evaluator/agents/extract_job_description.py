"""Agent for extracting structured job description from text."""

from resume_evaluator.llm import structured_completion
from resume_evaluator.schemas import JobDescription


def extract_job_description(job_description_text: str) -> JobDescription:
    """
    Extract structured job description from text.

    Args:
        job_description_text: Raw job description text.

    Returns:
        Structured JobDescription.
    """
    system_prompt = """You are an expert at parsing job descriptions and extracting structured information.
Extract all relevant information from the job description text and structure it according to the schema.
Be thorough and accurate. If information is not available, use appropriate defaults (empty lists, None, etc.)."""

    user_content = f"""Extract the job description details from the following text:

{job_description_text}"""

    return structured_completion(
        schema_model=JobDescription,
        system_prompt=system_prompt,
        user_content=user_content,
    )

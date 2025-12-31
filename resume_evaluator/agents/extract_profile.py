"""Agent for extracting candidate profile from resume text."""

from resume_evaluator.llm import structured_completion
from resume_evaluator.schemas import CandidateProfile


def extract_candidate_profile(resume_text: str) -> CandidateProfile:
    """
    Extract structured candidate profile from resume text.

    Args:
        resume_text: Raw text extracted from resume.

    Returns:
        Structured CandidateProfile.
    """
    system_prompt = """You are an expert at parsing resumes and extracting structured information.
Extract all relevant information from the resume text and structure it according to the schema.
Be thorough and accurate. If information is not available, use appropriate defaults (empty lists, None, etc.)."""

    user_content = f"""Extract the candidate profile from the following resume text:

{resume_text}"""

    return structured_completion(
        schema_model=CandidateProfile,
        system_prompt=system_prompt,
        user_content=user_content,
    )

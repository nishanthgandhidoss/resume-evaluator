"""Agent for evaluating candidate fit for a job."""

from resume_evaluator.llm import structured_completion
from resume_evaluator.schemas import CandidateProfile, FitEvaluation, JobDescription


def evaluate_fit(
    candidate_profile: CandidateProfile, job_description: JobDescription
) -> FitEvaluation:
    """
    Evaluate candidate fit for the job.

    Args:
        candidate_profile: Structured candidate profile.
        job_description: Structured job description.

    Returns:
        FitEvaluation with score and detailed analysis.
    """
    system_prompt = """You are an expert recruiter evaluating a candidate's fit for a job.
Analyze the candidate profile against the job description and provide a comprehensive evaluation.
The fit_score should be an integer from 0 to 100 representing the overall fit.
Set is_fit to true if fit_score >= 70, false otherwise.
Be thorough in identifying strengths, gaps, and providing actionable recommendations."""

    user_content = f"""Evaluate the candidate's fit for this job:

CANDIDATE PROFILE:
{candidate_profile.model_dump_json(indent=2)}

JOB DESCRIPTION:
{job_description.model_dump_json(indent=2)}

Provide a detailed evaluation including:
- Fit score (0-100)
- Whether they are a fit (score >= 70)
- Summary of fit
- Key strengths
- Gaps or missing qualifications
- Recommendations for improvement
- Missing keywords from the job description
- Any risk flags or concerns"""

    evaluation = structured_completion(
        schema_model=FitEvaluation,
        system_prompt=system_prompt,
        user_content=user_content,
    )

    # Ensure is_fit is correctly set based on fit_score
    evaluation.is_fit = evaluation.fit_score >= 70

    return evaluation

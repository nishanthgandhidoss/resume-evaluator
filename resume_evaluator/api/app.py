"""FastAPI application for resume evaluation API."""

from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from resume_evaluator.pipeline.graph import run_evaluation
from resume_evaluator.schemas import EvaluationResult

app = FastAPI(
    title="Resume Evaluator API",
    description="API for evaluating resume fit against job descriptions",
    version="0.1.0",
)


class EvaluateRequest(BaseModel):
    """Request model for JSON-based evaluation."""

    resume_text: Optional[str] = None
    job_description_text: str


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Status dictionary.
    """
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvaluationResult)
async def evaluate_resume(
    resume: Optional[UploadFile] = File(None),
    job_description: Optional[str] = Form(None),
    resume_text: Optional[str] = Form(None),
    job_description_text: Optional[str] = Form(None),
) -> EvaluationResult:
    """
    Evaluate resume against job description.

    Accepts either:
    - multipart/form-data with 'resume' file and 'job_description' field
    - multipart/form-data with 'resume_text' and 'job_description_text' fields
    - JSON body with EvaluateRequest

    Args:
        resume: PDF file upload (optional).
        job_description: Job description text from form (optional).
        resume_text: Resume text from form (optional).
        job_description_text: Job description text from form (optional).

    Returns:
        EvaluationResult with candidate profile, job description, and evaluation.

    Raises:
        HTTPException: If required inputs are missing or evaluation fails.
    """
    # Determine job description text
    jd_text = job_description or job_description_text
    if not jd_text:
        raise HTTPException(
            status_code=400,
            detail="job_description or job_description_text is required",
        )

    # Determine resume input
    resume_pdf_bytes: bytes | None = None
    resume_text_input: str | None = resume_text

    if resume:
        if resume.content_type not in ["application/pdf", None]:
            raise HTTPException(
                status_code=400, detail="Resume file must be a PDF"
            )
        resume_pdf_bytes = await resume.read()

    if not resume_pdf_bytes and not resume_text_input:
        raise HTTPException(
            status_code=400,
            detail="Either resume file or resume_text must be provided",
        )

    try:
        result = run_evaluation(
            resume_pdf_bytes=resume_pdf_bytes,
            resume_text=resume_text_input,
            job_description_text=jd_text,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Evaluation failed: {str(e)}"
        ) from e


@app.post("/evaluate/json", response_model=EvaluationResult)
async def evaluate_resume_json(request: EvaluateRequest) -> EvaluationResult:
    """
    Evaluate resume against job description (JSON body).

    Args:
        request: EvaluateRequest with resume_text and job_description_text.

    Returns:
        EvaluationResult with candidate profile, job description, and evaluation.

    Raises:
        HTTPException: If required inputs are missing or evaluation fails.
    """
    if not request.job_description_text:
        raise HTTPException(
            status_code=400, detail="job_description_text is required"
        )

    if not request.resume_text:
        raise HTTPException(
            status_code=400, detail="resume_text is required for JSON endpoint"
        )

    try:
        result = run_evaluation(
            resume_text=request.resume_text,
            job_description_text=request.job_description_text,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Evaluation failed: {str(e)}"
        ) from e

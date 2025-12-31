"""Tests for the evaluation pipeline."""

from unittest.mock import patch

import pytest

from resume_evaluator.agents.evaluate_fit import evaluate_fit
from resume_evaluator.agents.extract_job_description import (
    extract_job_description,
)
from resume_evaluator.agents.extract_profile import extract_candidate_profile
from resume_evaluator.pipeline.graph import run_evaluation
from resume_evaluator.schemas import (
    CandidateProfile,
    Education,
    FitEvaluation,
    JobDescription,
    Project,
    Role,
)


@pytest.fixture
def mock_candidate_profile() -> CandidateProfile:
    """Create a mock candidate profile for testing."""
    return CandidateProfile(
        name="John Doe",
        email="john.doe@example.com",
        summary="Experienced software engineer",
        skills_primary=["Python", "FastAPI", "Docker"],
        skills_secondary=["Communication", "Teamwork"],
        education=[
            Education(
                institution="University of Example",
                degree="BS Computer Science",
                graduation_year=2020,
            )
        ],
        work_experience=[
            Role(
                title="Software Engineer",
                company="Tech Corp",
                description="Developed web applications",
                start_date="2020-01",
                end_date="Present",
            )
        ],
        projects=[
            Project(
                name="Resume Evaluator",
                description="AI-powered resume evaluation system",
                technologies=["Python", "FastAPI"],
            )
        ],
        keywords=["Python", "FastAPI", "Docker", "Software Engineering"],
    )


@pytest.fixture
def mock_job_description() -> JobDescription:
    """Create a mock job description for testing."""
    return JobDescription(
        title="Senior Software Engineer",
        company="Tech Corp",
        summary="Looking for an experienced software engineer",
        responsibilities=["Develop web applications", "Lead technical projects"],
        required_skills=["Python", "FastAPI", "Docker"],
        preferred_skills=["Kubernetes", "AWS"],
        qualifications=["5+ years experience", "BS in Computer Science"],
        seniority="Senior",
        keywords=["Python", "FastAPI", "Docker", "Senior", "Leadership"],
    )


@pytest.fixture
def mock_fit_evaluation() -> FitEvaluation:
    """Create a mock fit evaluation for testing."""
    return FitEvaluation(
        fit_score=75,
        is_fit=True,
        fit_summary="Good fit with strong technical skills",
        strengths=["Strong Python experience", "Relevant project work"],
        gaps=["Missing Kubernetes experience", "Less seniority than preferred"],
        recommendations=["Gain Kubernetes experience", "Highlight leadership experience"],
        missing_keywords=["Kubernetes"],
        risk_flags=[],
    )


@patch("resume_evaluator.agents.extract_profile.structured_completion")
def test_extract_candidate_profile(
    mock_llm, mock_candidate_profile: CandidateProfile
) -> None:
    """Test candidate profile extraction."""
    mock_llm.return_value = mock_candidate_profile

    result = extract_candidate_profile("Sample resume text")
    assert result.name == "John Doe"
    assert "Python" in result.skills_primary
    mock_llm.assert_called_once()


@patch("resume_evaluator.agents.extract_job_description.structured_completion")
def test_extract_job_description(
    mock_llm, mock_job_description: JobDescription
) -> None:
    """Test job description extraction."""
    mock_llm.return_value = mock_job_description

    result = extract_job_description("Sample job description")
    assert result.title == "Senior Software Engineer"
    assert "Python" in result.required_skills
    mock_llm.assert_called_once()


@patch("resume_evaluator.agents.evaluate_fit.structured_completion")
def test_evaluate_fit(
    mock_llm,
    mock_candidate_profile: CandidateProfile,
    mock_job_description: JobDescription,
    mock_fit_evaluation: FitEvaluation,
) -> None:
    """Test fit evaluation."""
    mock_llm.return_value = mock_fit_evaluation

    result = evaluate_fit(mock_candidate_profile, mock_job_description)
    assert result.fit_score == 75
    assert result.is_fit is True
    assert len(result.strengths) > 0
    mock_llm.assert_called_once()


@patch("resume_evaluator.pipeline.graph.extract_text_from_pdf")
@patch("resume_evaluator.pipeline.graph.extract_candidate_profile")
@patch("resume_evaluator.pipeline.graph.extract_job_description")
@patch("resume_evaluator.pipeline.graph.evaluate_fit")
def test_run_evaluation(
    mock_evaluate,
    mock_extract_jd,
    mock_extract_profile,
    mock_extract_pdf,
    mock_candidate_profile: CandidateProfile,
    mock_job_description: JobDescription,
    mock_fit_evaluation: FitEvaluation,
) -> None:
    """Test complete evaluation pipeline."""
    mock_extract_pdf.return_value = "Sample resume text"
    mock_extract_profile.return_value = mock_candidate_profile
    mock_extract_jd.return_value = mock_job_description
    mock_evaluate.return_value = mock_fit_evaluation

    result = run_evaluation(
        resume_pdf_bytes=b"fake pdf bytes",
        job_description_text="Sample job description",
    )

    assert result.candidate_profile.name == "John Doe"
    assert result.job_description.title == "Senior Software Engineer"
    assert result.evaluation.fit_score == 75
    assert result.evaluation.is_fit is True

    mock_extract_pdf.assert_called_once()
    mock_extract_profile.assert_called_once()
    mock_extract_jd.assert_called_once()
    mock_evaluate.assert_called_once()


def test_run_evaluation_with_text() -> None:
    """Test evaluation with resume text instead of PDF."""
    with patch("resume_evaluator.pipeline.graph.extract_candidate_profile") as mock_profile, \
         patch("resume_evaluator.pipeline.graph.extract_job_description") as mock_jd, \
         patch("resume_evaluator.pipeline.graph.evaluate_fit") as mock_eval:

        mock_profile.return_value = CandidateProfile(
            summary="Test candidate",
            skills_primary=["Python"],
        )
        mock_jd.return_value = JobDescription(
            title="Software Engineer",
            summary="Test job",
            required_skills=["Python"],
        )
        mock_eval.return_value = FitEvaluation(
            fit_score=80,
            is_fit=True,
            fit_summary="Good fit",
        )

        result = run_evaluation(
            resume_text="Sample resume text",
            job_description_text="Sample job description",
        )

        assert result.evaluation.fit_score == 80
        mock_profile.assert_called_once()
        mock_jd.assert_called_once()
        mock_eval.assert_called_once()

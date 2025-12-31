"""Pydantic schemas for resume evaluation."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Education(BaseModel):
    """Education entry model."""

    institution: str = Field(..., description="Name of the educational institution")
    degree: str = Field(..., description="Degree obtained")
    field_of_study: Optional[str] = Field(None, description="Field of study")
    graduation_year: Optional[int] = Field(None, description="Year of graduation")
    gpa: Optional[float] = Field(None, description="GPA if available")


class Role(BaseModel):
    """Work role/position model."""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM or YYYY)")
    end_date: Optional[str] = Field(
        None, description="End date (YYYY-MM or YYYY) or 'Present'"
    )
    location: Optional[str] = Field(None, description="Job location")
    description: str = Field(..., description="Role description and responsibilities")
    achievements: Optional[List[str]] = Field(
        None, description="Key achievements in this role"
    )


class Project(BaseModel):
    """Project entry model."""

    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    technologies: Optional[List[str]] = Field(None, description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL if available")
    role: Optional[str] = Field(None, description="Role in the project")


class CandidateProfile(BaseModel):
    """Structured candidate profile extracted from resume."""

    name: Optional[str] = Field(None, description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Location")
    years_experience: Optional[float] = Field(
        None, description="Years of professional experience"
    )
    summary: str = Field(..., description="Professional summary")
    skills_primary: List[str] = Field(
        default_factory=list, description="Primary/technical skills"
    )
    skills_secondary: List[str] = Field(
        default_factory=list, description="Secondary/soft skills"
    )
    certifications: Optional[List[str]] = Field(
        None, description="Professional certifications"
    )
    education: List[Education] = Field(
        default_factory=list, description="Education history"
    )
    work_experience: List[Role] = Field(
        default_factory=list, description="Work experience"
    )
    projects: List[Project] = Field(default_factory=list, description="Projects")
    keywords: List[str] = Field(
        default_factory=list, description="Relevant keywords extracted from resume"
    )


class JobDescription(BaseModel):
    """Structured job description model."""

    title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    summary: str = Field(..., description="Job summary")
    responsibilities: List[str] = Field(
        default_factory=list, description="Key responsibilities"
    )
    required_skills: List[str] = Field(
        default_factory=list, description="Required skills"
    )
    preferred_skills: List[str] = Field(
        default_factory=list, description="Preferred skills"
    )
    qualifications: List[str] = Field(
        default_factory=list, description="Required qualifications"
    )
    seniority: Optional[str] = Field(
        None, description="Seniority level (e.g., Junior, Mid, Senior)"
    )
    keywords: List[str] = Field(
        default_factory=list, description="Relevant keywords from job description"
    )


class FitEvaluation(BaseModel):
    """Evaluation of candidate fit for the job."""

    fit_score: int = Field(
        ..., ge=0, le=100, description="Fit score from 0 to 100"
    )
    is_fit: bool = Field(..., description="Whether candidate is a fit (score >= 70)")
    fit_summary: str = Field(..., description="Summary of fit assessment")
    strengths: List[str] = Field(
        default_factory=list, description="Candidate strengths for this role"
    )
    gaps: List[str] = Field(
        default_factory=list, description="Gaps or missing qualifications"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for improvement"
    )
    missing_keywords: List[str] = Field(
        default_factory=list, description="Important keywords missing from resume"
    )
    risk_flags: List[str] = Field(
        default_factory=list, description="Potential risk flags or concerns"
    )


class EvaluationResult(BaseModel):
    """Complete evaluation result."""

    candidate_profile: CandidateProfile
    job_description: JobDescription
    evaluation: FitEvaluation

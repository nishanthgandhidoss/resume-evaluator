"""LangGraph pipeline for resume evaluation."""

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from resume_evaluator.agents.evaluate_fit import evaluate_fit
from resume_evaluator.agents.extract_job_description import extract_job_description
from resume_evaluator.agents.extract_profile import extract_candidate_profile
from resume_evaluator.parsers.pdf import extract_text_from_pdf
from resume_evaluator.schemas import (
    CandidateProfile,
    EvaluationResult,
    FitEvaluation,
    JobDescription,
)


class EvaluationState(TypedDict):
    """State for the evaluation pipeline."""

    resume_pdf_bytes: bytes | None
    resume_text: str | None
    job_description_text: str
    candidate_profile: CandidateProfile | None
    job_description: JobDescription | None
    evaluation: FitEvaluation | None


def parse_resume_node(state: EvaluationState) -> EvaluationState:
    """
    Parse resume from PDF if needed.

    Args:
        state: Current pipeline state.

    Returns:
        Updated state with resume_text.
    """
    if state.get("resume_text"):
        return state

    if not state.get("resume_pdf_bytes"):
        raise ValueError(
            "Either resume_text or resume_pdf_bytes must be provided"
        )

    resume_text = extract_text_from_pdf(state["resume_pdf_bytes"])
    state["resume_text"] = resume_text
    return state


def profile_node(state: EvaluationState) -> EvaluationState:
    """
    Extract candidate profile from resume text.

    Args:
        state: Current pipeline state.

    Returns:
        Updated state with candidate_profile.
    """
    if not state.get("resume_text"):
        raise ValueError("resume_text is required for profile extraction")

    candidate_profile = extract_candidate_profile(state["resume_text"])
    state["candidate_profile"] = candidate_profile
    return state


def job_node(state: EvaluationState) -> EvaluationState:
    """
    Extract job description from text.

    Args:
        state: Current pipeline state.

    Returns:
        Updated state with job_description.
    """
    if not state.get("job_description_text"):
        raise ValueError("job_description_text is required")

    job_description = extract_job_description(state["job_description_text"])
    state["job_description"] = job_description
    return state


def evaluate_node(state: EvaluationState) -> EvaluationState:
    """
    Evaluate fit between candidate and job.

    Args:
        state: Current pipeline state.

    Returns:
        Updated state with evaluation.
    """
    if not state.get("candidate_profile") or not state.get("job_description"):
        raise ValueError(
            "Both candidate_profile and job_description are required for evaluation"
        )

    evaluation = evaluate_fit(
        state["candidate_profile"], state["job_description"]
    )
    state["evaluation"] = evaluation
    return state


def build_evaluation_graph() -> Any:
    """
    Build the LangGraph state graph for evaluation.

    Returns:
        Compiled graph.
    """
    graph = StateGraph(EvaluationState)

    # Add nodes
    graph.add_node("parse_resume", parse_resume_node)
    graph.add_node("profile", profile_node)
    graph.add_node("job", job_node)
    graph.add_node("evaluate", evaluate_node)

    # Set entry point
    graph.set_entry_point("parse_resume")

    # Add edges
    graph.add_edge("parse_resume", "profile")
    graph.add_edge("profile", "job")
    graph.add_edge("job", "evaluate")
    graph.add_edge("evaluate", END)

    return graph.compile()


# Global compiled graph instance
_evaluation_graph: Any = None


def get_evaluation_graph() -> Any:
    """
    Get or create the compiled evaluation graph.

    Returns:
        Compiled graph instance.
    """
    global _evaluation_graph
    if _evaluation_graph is None:
        _evaluation_graph = build_evaluation_graph()
    return _evaluation_graph


def run_evaluation(
    resume_pdf_bytes: bytes | None = None,
    resume_text: str | None = None,
    job_description_text: str = "",
) -> EvaluationResult:
    """
    Run the complete evaluation pipeline.

    Args:
        resume_pdf_bytes: PDF file bytes (optional if resume_text provided).
        resume_text: Resume text (optional if resume_pdf_bytes provided).
        job_description_text: Job description text (required).

    Returns:
        Complete EvaluationResult.

    Raises:
        ValueError: If required inputs are missing or pipeline fails.
    """
    if not job_description_text:
        raise ValueError("job_description_text is required")

    if not resume_pdf_bytes and not resume_text:
        raise ValueError(
            "Either resume_pdf_bytes or resume_text must be provided"
        )

    graph = get_evaluation_graph()

    initial_state: EvaluationState = {
        "resume_pdf_bytes": resume_pdf_bytes,
        "resume_text": resume_text,
        "job_description_text": job_description_text,
        "candidate_profile": None,
        "job_description": None,
        "evaluation": None,
    }

    final_state = graph.invoke(initial_state)

    if (
        not final_state.get("candidate_profile")
        or not final_state.get("job_description")
        or not final_state.get("evaluation")
    ):
        raise ValueError("Pipeline failed to produce complete evaluation")

    return EvaluationResult(
        candidate_profile=final_state["candidate_profile"],
        job_description=final_state["job_description"],
        evaluation=final_state["evaluation"],
    )

"""Streamlit UI for resume evaluation."""

import json

import streamlit as st

from resume_evaluator.pipeline.graph import run_evaluation
from resume_evaluator.schemas import EvaluationResult

st.set_page_config(
    page_title="Resume Evaluator",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Resume Evaluator")
st.markdown(
    """
    Upload a resume PDF and provide a job description to evaluate the candidate's fit.
    """
)

# File upload
resume_file = st.file_uploader(
    "Upload Resume PDF", type=["pdf"], help="Upload the candidate's resume as a PDF"
)

# Job description input
job_description = st.text_area(
    "Job Description",
    height=200,
    help="Enter the job description text",
    placeholder="Paste the job description here...",
)

# Evaluate button
if st.button("Evaluate", type="primary"):
    if not job_description:
        st.error("Please provide a job description.")
    elif not resume_file:
        st.error("Please upload a resume PDF.")
    else:
        try:
            with st.spinner("Evaluating resume..."):
                # Read PDF bytes
                resume_bytes = resume_file.read()

                # Run evaluation
                result: EvaluationResult = run_evaluation(
                    resume_pdf_bytes=resume_bytes,
                    job_description_text=job_description,
                )

                # Display results
                st.success("Evaluation complete!")

                # Fit score and status
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Fit Score",
                        f"{result.evaluation.fit_score}/100",
                        delta=f"{result.evaluation.fit_score - 70}",
                        delta_color="normal" if result.evaluation.is_fit else "inverse",
                    )
                with col2:
                    fit_status = "✅ Good Fit" if result.evaluation.is_fit else "❌ Not a Fit"
                    st.metric("Fit Status", fit_status)

                # Summary
                st.subheader("Fit Summary")
                st.write(result.evaluation.fit_summary)

                # Strengths and Gaps
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Strengths")
                    if result.evaluation.strengths:
                        for strength in result.evaluation.strengths:
                            st.write(f"• {strength}")
                    else:
                        st.write("None identified")

                with col2:
                    st.subheader("Gaps")
                    if result.evaluation.gaps:
                        for gap in result.evaluation.gaps:
                            st.write(f"• {gap}")
                    else:
                        st.write("None identified")

                # Recommendations
                st.subheader("Recommendations")
                if result.evaluation.recommendations:
                    for rec in result.evaluation.recommendations:
                        st.write(f"• {rec}")
                else:
                    st.write("None")

                # Missing keywords
                if result.evaluation.missing_keywords:
                    st.subheader("Missing Keywords")
                    st.write(", ".join(result.evaluation.missing_keywords))

                # Risk flags
                if result.evaluation.risk_flags:
                    st.subheader("⚠️ Risk Flags")
                    for flag in result.evaluation.risk_flags:
                        st.warning(flag)

                # Expandable JSON view
                with st.expander("View Full JSON Result"):
                    st.json(result.model_dump(mode="json"))

        except ValueError as e:
            st.error(f"Validation error: {str(e)}")
        except Exception as e:
            st.error(f"Evaluation failed: {str(e)}")
            st.exception(e)

"""Streamlit frontend for CV-Maxxing: upload a CV PDF + paste a job
description, hit the FastAPI backend, and render the structured report."""
import os

import requests
import streamlit as st


def _get_backend_url() -> str:
    """Streamlit Community Cloud secrets (set via the app's Secrets panel)
    take priority; falls back to a plain env var for local/Docker use."""
    try:
        if "BACKEND_URL" in st.secrets:
            return st.secrets["BACKEND_URL"]
    except Exception:
        pass
    return os.getenv("BACKEND_URL", "http://localhost:8000")


BACKEND_URL = _get_backend_url()

st.set_page_config(page_title="CV-Maxxing - CV / job-fit analyser", page_icon="📄")
st.title("📄 CV-Maxxing")
st.caption("Upload a CV (PDF) and a job description to get a structured skills-gap report.")

tab_analyze, tab_history = st.tabs(["Analyze", "History"])

with tab_analyze:
    cv_file = st.file_uploader("CV (PDF)", type=["pdf"])
    job_description = st.text_area("Job description", height=220)
    submitted = st.button("Analyze", type="primary", disabled=not (cv_file and job_description))

    if submitted:
        with st.spinner("Calling Gemini..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/analyze",
                    files={"cv_file": (cv_file.name, cv_file.getvalue(), "application/pdf")},
                    data={"job_description": job_description},
                    timeout=60,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                st.error(f"Request failed: {exc}")
            else:
                payload = response.json()
                result = payload["result"]
                usage = payload["usage"]

                st.metric("ATS match score", f"{result['ats_match_score']}/100")
                st.write(result["summary"])

                st.subheader("Skill gaps")
                for gap in result["skill_gaps"]:
                    icon = "✅" if gap["present_in_cv"] else "⚠️"
                    st.markdown(f"{icon} **{gap['skill']}**")
                    if gap.get("evidence"):
                        st.caption(f"Evidence: {gap['evidence']}")
                    if gap.get("suggestion"):
                        st.caption(f"Suggestion: {gap['suggestion']}")

                if result["missing_keywords"]:
                    st.subheader("Missing keywords")
                    st.write(", ".join(result["missing_keywords"]))

                if result["bullet_rewrites"]:
                    st.subheader("Bullet rewrite suggestions")
                    for rewrite in result["bullet_rewrites"]:
                        st.markdown(f"- ~~{rewrite['original']}~~")
                        st.markdown(f"  → **{rewrite['rewritten']}**")
                        st.caption(rewrite["rationale"])

                st.subheader("Usage")
                st.json(usage)

with tab_history:
    st.button("Refresh")
    try:
        response = requests.get(f"{BACKEND_URL}/api/history", timeout=20)
        response.raise_for_status()
        items = response.json()["items"]
        if items:
            st.table(items)
        else:
            st.info("No analyses yet.")
    except requests.RequestException as exc:
        st.error(f"Could not load history: {exc}")

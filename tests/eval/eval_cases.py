"""Hand-written CV/JD pairs with a human-judged expected score *range* and
rationale, used by run_eval.py to sanity-check the pipeline's output
against informal human judgment. This is a small, hand-checked eval set,
not a rigorous benchmark -- see README.md's "Eval" section for why that's
still worth having."""
from dataclasses import dataclass


@dataclass
class EvalCase:
    name: str
    cv_text: str
    job_description: str
    expected_score_range: tuple
    rationale: str


JD_BACKEND = """
Backend Engineer. Requirements: 3+ years Python (FastAPI/Django), strong
Postgres, AWS (Lambda/S3/RDS), Docker (Kubernetes a plus), automated testing,
CI/CD (GitHub Actions). Nice to have: Terraform, Kafka/SQS.
"""

CASES = [
    EvalCase(
        name="partial_match_backend",
        cv_text="""
Alex Morgan
Software Engineer

Experience:
- Software Engineer, Northbridge Fintech (Jul 2024 - Present): worked on the
  company's API, helped fix signup-flow bugs, wrote some backend tests, used
  Postgres for the database.
- Junior Developer, Pixel & Co (Sep 2023 - Jun 2024): built a React dashboard,
  did code reviews, set up Docker for local dev.

Skills: Python, FastAPI, Flask, PostgreSQL, Git, Docker, React (basic), pytest
""",
        job_description=JD_BACKEND,
        expected_score_range=(40, 70),
        rationale=(
            "Confirmed against a real run (scored 60): Python/FastAPI/Postgres/"
            "Docker/testing all present, but 2 years (not 3+) and no AWS/CI-CD "
            "mentioned -- should land in the middle, not high and not near zero."
        ),
    ),
    EvalCase(
        name="strong_match_backend",
        cv_text="""
Priya Shah
Senior Backend Engineer, 5 years experience

Experience:
- Senior Backend Engineer, Fenwick Logistics (2021-Present): designed and
  operated REST APIs in Python/FastAPI serving 2M+ requests/day; migrated the
  primary datastore to PostgreSQL on AWS RDS; deployed services on AWS Lambda
  and S3 for async processing; built the team's GitHub Actions CI/CD pipeline;
  containerised all services with Docker and Kubernetes.
- Backend Engineer, StartCo (2019-2021): wrote unit and integration tests
  (pytest) as part of normal development; used Terraform for infrastructure.

Skills: Python, FastAPI, PostgreSQL, AWS (Lambda, S3, RDS), Docker, Kubernetes,
GitHub Actions, Terraform, pytest
""",
        job_description=JD_BACKEND,
        expected_score_range=(80, 100),
        rationale=(
            "Every explicit requirement is directly stated in the CV, including "
            "the 'nice to have' Terraform. Should score high."
        ),
    ),
    EvalCase(
        name="domain_mismatch",
        cv_text="""
Sam Carter
Marketing Coordinator, 4 years experience

Experience:
- Marketing Coordinator, BrightAds (2021-Present): ran social media campaigns,
  wrote copy for email newsletters, analysed campaign performance in Google
  Analytics and Excel, coordinated with design agencies.
- Marketing Assistant, LocalBrand Co (2020-2021): managed the Instagram
  account, organised in-store promotional events.

Skills: Content writing, Google Analytics, Excel, Canva, email marketing,
event coordination
""",
        job_description=JD_BACKEND,
        expected_score_range=(0, 20),
        rationale=(
            "No technical overlap at all with the JD's requirements -- should "
            "score near zero, not a moderate 'benefit of the doubt' score."
        ),
    ),
    EvalCase(
        name="adjacent_stack_mismatch",
        cv_text="""
Jordan Lee
Backend Engineer, 4 years experience

Experience:
- Backend Engineer, NodeWorks (2022-Present): built REST APIs in Node.js
  (Express) and TypeScript, used MongoDB as the primary datastore, deployed
  on Google Cloud Run, wrote Jest tests, used CircleCI for CI/CD.
- Backend Developer, SmallCo (2020-2022): built internal tools in Node.js.

Skills: Node.js, Express, TypeScript, MongoDB, Google Cloud, Jest, CircleCI,
Docker
""",
        job_description=JD_BACKEND,
        expected_score_range=(15, 40),
        rationale=(
            "Same discipline (backend engineering) and some transferable "
            "concepts (REST APIs, Docker, automated testing, CI/CD) but the "
            "specific required stack -- Python, Postgres, AWS -- is entirely "
            "absent. Should score low but not zero, since the transferable "
            "concepts are real."
        ),
    ),
]

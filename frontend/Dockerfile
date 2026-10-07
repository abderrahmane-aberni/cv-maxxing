# Build from the repo root: docker build -f frontend/Dockerfile .
FROM python:3.12-slim

WORKDIR /app

COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/streamlit_app.py .

EXPOSE 8501
# Shell form (not exec/JSON form) so $PORT actually expands -- Render
# assigns a dynamic port the container must bind to.
CMD streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}

# Use official Python image
FROM python:3.11-slim

# Set workdir to root of project
WORKDIR /app

# Copy everything into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

ENV PYTHONPATH=/app

# Run Streamlit
CMD ["streamlit", "run", "ui/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

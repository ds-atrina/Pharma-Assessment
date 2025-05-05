# Use an official Python runtime
FROM python:3.10-slim

# Expose the Streamlit port
EXPOSE 8501

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code and config files
WORKDIR /app
COPY . .

# Launch Streamlit
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

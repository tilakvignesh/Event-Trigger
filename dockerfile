#  Use the official Python image
FROM python:3.10

#  Set working directory inside the container
WORKDIR /app

# Copy only `requirements.txt` first (for caching layers)
COPY requirements.txt .

#  Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

#  Copy all project files AFTER dependencies are installed
COPY . .

# Ensure `.env` is included inside the container
COPY .env .env

#  Expose FastAPI port
EXPOSE 8000

# This ensures FastAPI runs inside Docker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

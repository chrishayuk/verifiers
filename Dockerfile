FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy the app
COPY . .

# expose the port
EXPOSE 8000

# startup
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

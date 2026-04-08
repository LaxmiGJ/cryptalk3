FROM python:3.12

WORKDIR /app

COPY requirements-hf.txt .

RUN pip install -r requirements-hf.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
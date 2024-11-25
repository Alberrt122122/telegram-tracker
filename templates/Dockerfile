FROM python:3.9.6-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_ENV=production

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000"]

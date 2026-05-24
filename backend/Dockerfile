FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m venv venv

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app
EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["uvicorn", "src.main:app", "--host",  "0.0.0.0", "--port", "8000"]
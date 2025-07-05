FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install telethon requests

CMD ["python3", "parser.py"]
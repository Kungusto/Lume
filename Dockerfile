FROM python:3.12.9

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app
COPY start.sh /app/start.sh

ENV PYTHONPATH=/app

RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
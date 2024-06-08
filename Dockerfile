FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY wait-for-it.sh /usr/wait-for-it.sh
RUN chmod +x /usr/wait-for-it.sh

COPY . /app

CMD ["/usr/wait-for-it.sh", "postgres-container:5432", "--", "python", "app.py"]

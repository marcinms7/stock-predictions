FROM python:3.7.4-slim-buster

USER root
ENV PYTHONUNBUFFERED 1

WORKDIR /app
ADD . /app
COPY . /requirements.txt /run/requirements.txt

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

EXPOSE 8050

CMD ["python3", "interactive_stocks_graphs2.py"]

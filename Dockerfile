FROM python:3.6
ENV PYTHONUNBUFFERED=1
RUN mkdir -p /code/log/gunicorn
ADD .  /code/
RUN pip install -r /code/requirements.txt
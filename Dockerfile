FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install pip -U && \
    pip install --no-cache-dir -r requirements.txt -U
ADD . /code/

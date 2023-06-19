# Start with Python 3.11 base image
FROM python:3.11.2-slim
RUN apt-get update && apt-get install --no-install-recommends -y bash nano mc build-essential

RUN mkdir /server
WORKDIR /server
COPY . /server/

RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/server/src/fastapi_app/rest"
EXPOSE 4747

CMD uvicorn server:app --host 0.0.0.0 --port 4747
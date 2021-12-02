FROM python:3.10-alpine

EXPOSE 8000
WORKDIR /opt/balthify2/src

RUN apk add --no-cache \
  g++ \
  musl-dev

COPY requirements2.txt .
RUN pip install --no-cache-dir -r requirements2.txt

COPY balthify2 /opt/balthify2/src/balthify2

CMD ["python", "-m", "balthify2.tgbot"]

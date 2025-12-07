FROM python:3.11-slim

WORKDIR /app

# requirements는 api 폴더에서 가져와야 함!!
COPY ./api/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# api 전체를 /app 안으로 복사
COPY ./api /app

EXPOSE 8000

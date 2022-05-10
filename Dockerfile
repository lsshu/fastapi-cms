FROM python:3.8
WORKDIR /app
EXPOSE 80
RUN mkdir -p /app && pip install lsshu-cms
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
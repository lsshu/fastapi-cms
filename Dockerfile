FROM python:3.8
RUN mkdir -p /app && pip install uvicorn fastapi sqlalchemy sqlalchemy_mptt python-multipart hashids passlib python-jose bcrypt websockets
EXPOSE 80
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
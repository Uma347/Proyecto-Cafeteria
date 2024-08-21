FROM python:3.9-bullseye
WORKDIR /app
COPY ./app /app
EXPOSE 3000
RUN pip install -r requirements.txt
CMD python app.py
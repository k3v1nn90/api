FROM python:3
ADD . /app
WORKDIR /app
RUN apt-get update
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 5000
ENV STAGE 'dev'
CMD ["python", "app.py"]

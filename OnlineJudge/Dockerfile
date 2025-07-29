FROM python:3.11

WORKDIR /OJ
COPY . /OJ
RUN apt update && apt install -y \
    g++ \
    openjdk-17-jdk \
    python3
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=OnlineJudge.settings
ENV PYTHONUNBUFFERED=1
 
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
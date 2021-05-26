FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED=1
COPY . ./app
WORKDIR /app

# Install dependencies:
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run the application:
#RUN ls
#RUN pip list

#EXPOSE 8000
#ENTRYPOINT [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]

# Run container on port 8000:8000 - django works on port 8000
# sudo docker run --name [container's name] -p 8000:8000 [image name]


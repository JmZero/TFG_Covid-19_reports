# set base image (host OS)
FROM python:3.8.0-slim

#RUN apk update && apk add libressl-dev postgresql-dev libffi-dev gcc musl-dev python3-dev

# set the working directory in the container
WORKDIR /bot

# copy the content of the local src directory to the working directory
COPY . /bot

# install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache -r requirements.txt

# command to run on container start
CMD [ "python", "./covid_reports.py" ]

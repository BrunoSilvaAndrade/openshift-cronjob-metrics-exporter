FROM python:3.6
#RECEIVE TIMEZONE PER PARAM OR SET DEFAULT VALUE
ARG timezoneName=Europe/Belfast
RUN rm -f /etc/localtime
RUN ln -s /usr/share/zoneinfo/${timezoneName} /etc/localtime
RUN mkdir -p /app
WORKDIR /app
COPY . ./
RUN pip install -r requirements.txt 
CMD ["python", "app.py"]

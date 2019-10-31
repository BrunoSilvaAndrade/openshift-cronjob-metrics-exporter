FROM python:3.6
ENV TZ=America/Sao_Paulo
RUN echo ${TZ} > /etc/timezone
RUN mkdir -p /app
WORKDIR /app
COPY . ./
RUN pip install -r requirements.txt 
CMD ["python", "app.py"]

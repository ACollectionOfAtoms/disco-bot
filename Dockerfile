FROM python:3.6.5
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD . /
ENV DISCO_TOKEN=$DISCO_TOKEN
ENV WEATHER_API_KEY=$WEATHER_API_KEY
ENV NYT_KEY=$NYT_KEY
CMD ["python", "./bot.py"]

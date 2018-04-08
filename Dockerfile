FROM python:3.6.5
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD bot.py /
ENV DISCO_TOKEN=$DISCO_TOKEN
CMD ["python", "./bot.py"]

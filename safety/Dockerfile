FROM python:slim-buster

WORKDIR /app

COPY requirements.txt /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt 

COPY . /app

EXPOSE 80

ENTRYPOINT [ "python" ]

CMD [ "./hello.py" ]

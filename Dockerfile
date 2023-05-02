FROM python:3.11-buster

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir pipenv

RUN pipenv install --system --deploy --clear

RUN pip uninstall pipenv -y

COPY . ./

CMD [ "python3", "app.py" ]

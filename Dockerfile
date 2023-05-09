FROM python:3.11-slim-buster


ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

ENV PYDEVD_DISABLE_FILE_VALIDATION=1

WORKDIR /app

# ENV FLASK_APP=app.py
# ENV FLASK_ENV=development

COPY Pipfile Pipfile.lock ./

RUN python -m pip install --upgrade pip

RUN pip install flask-migrate

RUN pip install --no-cache-dir pipenv

RUN pipenv install --dev --system --deploy --clear

RUN pip uninstall pipenv -y

# RUN flask db init
# RUN flask db migrate
# RUN flask db upgrade

COPY . ./

CMD [ "python3", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "flask", "run", "--host=0.0.0.0" ]


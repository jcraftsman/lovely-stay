FROM python:3.11-alpine as requirements-stage
ARG POETRY_VERSION=1.7.1
WORKDIR /tmp
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with app


FROM python:3.11-alpine as final-stage
WORKDIR /code
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/app
WORKDIR /code/app
CMD ["uvicorn", "lovely_stay_paas_transaction_script.booking_api:app", "--host", "0.0.0.0", "--port", "80"]

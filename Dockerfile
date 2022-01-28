# Python base
# ############################################################
FROM python:3.9-slim-buster as python-base

RUN pip install -U pip 
RUN pip install setuptools wheel
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip install "cryptography<3.5"
RUN pip install "poetry>=1.1.12"

RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-dev --no-root
RUN poetry run pip install psycopg2-binary

RUN addgroup app --gid 10000 && \
    useradd --gid app \
            --shell /sbin/nologin \
            --no-create-home \
            --uid 10000 app

# Final build
# ############################################################
FROM python-base as final
            
COPY godaddy_dynamic_dns /godaddy_dynamic_dns
COPY entrypoint.sh /godaddy_dynamic_dns

WORKDIR /godaddy_dynamic_dns

USER 10000

EXPOSE 5000

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]

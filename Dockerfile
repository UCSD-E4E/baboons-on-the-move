FROM ubuntu:20.04 AS base
RUN apt update && apt upgrade -y
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    git
RUN apt-get install -y \
    python3 \
    python3-tk \
    python3-pip
RUN mkdir /app
COPY . /app
WORKDIR /app

FROM base as requirements
RUN pip install poetry
RUN poetry export --without-hashes -f requirements.txt --output requirements.txt

FROM base
COPY --from=requirements /app/requirements.txt /app
RUN pip install -r requirements.txt
ENV CLI_ACTIVE=1
CMD ["python3", "./cli.py", "run"]
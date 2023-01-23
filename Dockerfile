FROM python:slim-bullseye

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    curl \
    bwa \
    samtools \
    bcftools \
    freebayes \
    default-jre \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN mkdir /home/vendor

# Poetry for Python dependencies
RUN curl -sSL 'https://install.python-poetry.org' | python -

# Picard for alignments
RUN curl -sSL https://github.com/broadinstitute/picard/releases/download/2.27.5/picard.jar -o /home/vendor/picard-2.27.5.jar

ENV PATH="/root/.local/bin:$PATH"

# Creates and build the environment
COPY .env /home/
COPY poetry.toml /home/
COPY pyproject.toml /home/

WORKDIR /home/
RUN poetry install

# Builds and runs the project
COPY data data
COPY src src

CMD [ "poetry" , "run", "python", "src/main.py"]

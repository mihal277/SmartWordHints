FROM python:3.9-slim

RUN apt-get update
RUN apt-get -y install build-essential

RUN useradd --create-home -u 5002 smart_word_hints_test
USER smart_word_hints_test
WORKDIR /home/smart_word_hints_test
ENV PYTHON_LINTERS_BIN_PATH="/home/smart_word_hints_test/.local/bin"
ENV PATH="${PATH}:${PYTHON_LINTERS_BIN_PATH}"

COPY smart_word_hints_api/ smart_word_hints_api/
COPY scripts/ scripts/
COPY setup.cfg setup.cfg

RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir --user -r smart_word_hints_api/requirements/dev_requirements.txt

RUN python -m nltk.downloader $(cat smart_word_hints_api/requirements/nltk_modules.txt)
RUN python -m spacy download $(cat smart_word_hints_api/requirements/spacy_modules.txt)

CMD ["sh", "scripts/run_api_tests.sh"]
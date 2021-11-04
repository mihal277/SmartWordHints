FROM python:3.9-slim

RUN useradd --create-home -u 5002 smart_word_hints_test
USER smart_word_hints_test
WORKDIR /home/smart_word_hints_test
ENV PATH="${PATH}:/home/smart_word_hints_test/.local/bin"

COPY smart_word_hints_api/ smart_word_hints_api/
COPY scripts/ scripts/
COPY setup.cfg setup.cfg

RUN pip install --user -r smart_word_hints_api/requirements/dev_requirements.txt
RUN python -m nltk.downloader $(cat smart_word_hints_api/requirements/nltk_modules.txt)

CMD ["sh", "scripts/run_api_tests.sh"]
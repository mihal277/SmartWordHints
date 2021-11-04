FROM python:3.9-slim

COPY smart_word_hints_api/ smart_word_hints_api/
COPY scripts/ scripts/
COPY setup.cfg setup.cfg

RUN pip install -r smart_word_hints_api/requirements/dev_requirements.txt
RUN python -m nltk.downloader $(cat smart_word_hints_api/requirements/nltk_modules.txt)

CMD ["sh", "scripts/run_api_tests.sh"]
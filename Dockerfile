FROM python:3.10
COPY ./requirements.txt /arup/requirements.txt
COPY ./entrypoint.py /arup/entrypoint.py
COPY ./analysis-results-profile/templates /arup/templates
RUN python -m pip install -r /arup/requirements.txt
RUN chmod +x /arup/entrypoint.py

VOLUME /rocrateroot
ENTRYPOINT ["/arup/entrypoint.py"]

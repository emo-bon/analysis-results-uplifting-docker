FROM python:3.10
COPY . /arup
RUN python -m pip install -r /arup/requirements.txt
RUN chmod +x /arup/entrypoint.py

VOLUME /rocrateroot
ENTRYPOINT ["/arup/entrypoint.py"]

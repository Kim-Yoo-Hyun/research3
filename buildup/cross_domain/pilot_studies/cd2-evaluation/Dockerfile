FROM python:3.11.14-slim-bookworm@sha256:65a93d69fa75478d554f4ad27c85c1e69fa184956261b4301ebaf6dbb0a3543d
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
LABEL org.research3.workspace="/home/yoohyun/research3" org.research3.study="cd2-evaluation"
COPY requirements.lock /opt/requirements.lock
COPY run.py verify.py protocol.json /study/
WORKDIR /study
ENTRYPOINT ["python"]

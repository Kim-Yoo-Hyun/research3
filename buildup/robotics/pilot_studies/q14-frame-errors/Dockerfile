FROM python:3.11.14-slim-bookworm@sha256:65a93d69fa75478d554f4ad27c85c1e69fa184956261b4301ebaf6dbb0a3543d
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
COPY requirements.lock /opt/requirements.lock
RUN pip install --no-cache-dir --only-binary=:all: -r /opt/requirements.lock --extra-index-url https://download.pytorch.org/whl/cpu && pip freeze --all > /opt/dependencies.lock
WORKDIR /study
ENTRYPOINT ["python"]

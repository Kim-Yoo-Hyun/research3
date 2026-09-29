FROM python:3.11.13-slim-bookworm@sha256:cec9aa7aa96eea4fa036e9b82be1e6b325f2e3707f462d885868df51ec0a4b47
COPY bootstrap.txt requirements.txt /recipe/
RUN python -m pip install --no-cache-dir --require-hashes --no-deps -r /recipe/bootstrap.txt \
 && python -m pip install --no-cache-dir --no-build-isolation --require-hashes --no-deps \
    --report /recipe/install.json -r /recipe/requirements.txt \
 && python -m pip check \
 && python -m pip freeze --all > /recipe/installed.txt
ENV PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MPLCONFIGDIR=/tmp/matplotlib SDL_VIDEODRIVER=dummy WANDB_MODE=disabled \
    PYTHONPATH=/source/rtc/src:/source/kinetix:/source/jaxued:/study
WORKDIR /study
ENTRYPOINT ["python", "-B", "-u"]

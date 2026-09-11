FROM python:3.11-slim-bookworm@sha256:b1add8a6f2aca6bcfcf0b9c9b522352f7ce0d62a3d556a2f2f32511aa0cca250
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libegl1 libglib2.0-0 libvulkan1 libgomp1 libx11-6 libxext6 libsm6 libice6 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir torch==2.7.1 --index-url https://download.pytorch.org/whl/cu128
COPY external/q8/ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8 /opt/ManiSkill
RUN pip install --no-cache-dir numpy==1.26.4 scipy==1.15.3 gymnasium==0.29.1 sapien==3.0.2 h5py==3.12.1 tensorboard==2.19.0 /opt/ManiSkill
RUN pip freeze --all > /opt/dependencies.lock && dpkg-query -W > /opt/os-packages.lock
WORKDIR /work

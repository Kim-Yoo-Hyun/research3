FROM python:3.11.14-slim-bookworm@sha256:65a93d69fa75478d554f4ad27c85c1e69fa184956261b4301ebaf6dbb0a3543d
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
LABEL org.research3.workspace="/home/yoohyun/research3" org.research3.study="q4-planning"
RUN rm /etc/apt/sources.list.d/debian.sources && \
    printf '%s\n' 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20260901T000000Z bookworm main' \
    'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20260901T000000Z bookworm-security main' > /etc/apt/sources.list && \
    apt-get -o Acquire::Check-Valid-Until=false update && \
    apt-get install -y --no-install-recommends build-essential cmake git ca-certificates flex bison && \
    mkdir -p /opt/environment && dpkg-query -W > /opt/environment/debian.lock && \
    rm -rf /var/lib/apt/lists/*
RUN git init /opt/downward && cd /opt/downward && \
    git remote add origin https://github.com/aibasel/downward.git && \
    git fetch --depth 1 origin 1eef26b2cbf599a1894606aa898d9d49e1034cb9 && \
    git checkout --detach FETCH_HEAD && python build.py release -j4
RUN git init /opt/val && cd /opt/val && \
    git remote add origin https://github.com/KCL-Planning/VAL.git && \
    git fetch --depth 1 origin 3c7a1f330bdab0ba28a4762bb45c3f06c27fb6d4 && \
    git checkout --detach FETCH_HEAD && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --target Validate -j4 && \
    ln -s /opt/val/build/bin/Validate /usr/local/bin/validate
RUN git -C /opt/downward rev-parse HEAD > /opt/environment/downward.commit && \
    git -C /opt/val rev-parse HEAD > /opt/environment/val.commit && \
    sha256sum /opt/downward/builds/release/bin/downward /opt/val/build/bin/Validate /opt/val/build/bin/libVAL.so > /opt/environment/binaries.sha256 && \
    python --version > /opt/environment/python.version
WORKDIR /study
ENTRYPOINT ["python"]

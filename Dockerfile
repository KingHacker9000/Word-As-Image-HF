FROM nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-dev git ffmpeg cmake build-essential \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/local/bin/python && \
    python -m pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN git clone https://github.com/BachiLi/diffvg.git /tmp/diffvg && \
    cd /tmp/diffvg && git submodule update --init --recursive && \
    FORCE_CUDA=1 python setup.py install && \
    cd /workspace && rm -rf /tmp/diffvg

COPY . /workspace

EXPOSE 7860
CMD ["python", "app.py"]

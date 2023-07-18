FROM ubuntu:22.04

RUN mkdir -p /workspace
WORKDIR /workspace
ENV HOME /workspace

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt -y update && apt -y install curl git build-essential libbz2-dev libdb-dev \
    libreadline-dev libffi-dev libgdbm-dev liblzma-dev \
    libncursesw5-dev libsqlite3-dev libssl-dev \
    zlib1g-dev uuid-dev tk-dev

ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/bin:$PATH

RUN curl https://pyenv.run | bash && \
    echo '' >> /workspace/.bashrc && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> /workspace/.bashrc && \
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> /workspace/.bashrc && \
    echo 'eval "$(pyenv init --path)"' >> /workspace/.bashrc && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> /workspace/.bashrc
RUN . /workspace/.bashrc && \
    PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.5 && \
    pyenv global 3.10.5 && \
    pip install -U pip

RUN apt -y install wget unzip libboost-all-dev cmake

RUN mkdir /opt/protobuf &&\
    cd /opt/protobuf &&\
    wget https://github.com/protocolbuffers/protobuf/releases/download/v3.17.3/protobuf-cpp-3.17.3.tar.gz &&\
    tar zxvf protobuf-cpp-3.17.3.tar.gz &&\
    cd protobuf-3.17.3 &&\
    ./configure &&\
    make -j9 &&\
    make install &&\
    rm -rf /opt/protobuf &&\
    ldconfig

RUN adduser --disabled-password --gecos "" --home /workspace ubuntu &&\
    echo "ubuntu:ubuntu" | chpasswd &&\
    chown ubuntu:ubuntu /workspace
USER ubuntu

COPY requirements.txt /workspace/
RUN . /workspace/.bashrc && python -m pip install -r requirements.txt

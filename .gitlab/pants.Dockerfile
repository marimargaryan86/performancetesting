# bullseye-slim
ARG REGISTRY
FROM ${REGISTRY}debian@sha256:d2285c63f42a27d633afa75929529c3761883faac292e7c1cf310d91c7399863
ENV PYENV_ROOT=/root/.pyenv PATH=/usr/local/go/bin:/root/.pyenv/bin:$PATH
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    gettext-base \
    git \
    gnupg \
    jq \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxmlsec1-dev \
    llvm \
    lsb-release \
    make \
    ssh \
    tk-dev \
    unzip \
    wget \
    xz-utils \
    zlib1g-dev \
&& curl -fsSL https://github.com/Tufin/oasdiff/releases/download/v1.2.3/oasdiff_1.2.3_linux_amd64.deb > /tmp/oasdiff.deb \
&& curl -fsSL https://sentry.io/get-cli/ | bash \
&& curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
&& curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
&& curl -fsSL https://github.com/fredwangwang/vscode-hcl-formatter/releases/download/0.4.0/hclfmt-linux > /usr/local/bin/hclfmt \
&& chmod +x /usr/local/bin/hclfmt \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list > /dev/null \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
&& apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    nomad \
    /tmp/oasdiff.deb \
&& curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
&& pyenv install 3.10.5 \
&& pyenv install 3.9.13 \
&& rm -rf /var/lib/apt/lists/* /tmp/oasdiff.deb \
&& pyenv global 3.10.5 3.9.13
COPY --from=golang:1.18.3 /usr/local/go/ /usr/local/go/

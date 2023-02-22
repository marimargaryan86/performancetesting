# bullseye-slim
ARG REGISTRY
FROM ${REGISTRY}debian@sha256:9b42b2e7eddd84eaddb67b45567cdc0e03ec826bf252352f300147cfb8ce5a6d
ENV PYENV_ROOT=/root/.pyenv PATH=/usr/local/go/bin:/root/.pyenv/bin:/root/.pyenv/shims:$PATH
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
&& curl -fsSL https://github.com/Tufin/oasdiff/releases/download/v1.3.1/oasdiff_1.3.1_linux_amd64.deb > /tmp/oasdiff.deb \
&& curl -fsSL https://sentry.io/get-cli/ | SENTRY_CLI_VERSION=2.12.0 bash \
&& curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
&& curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
&& curl -sfSL https://github.com/editorconfig-checker/editorconfig-checker/releases/download/2.7.0/ec-linux-amd64.tar.gz | tar xvz -C /usr/local bin/ec-linux-amd64 \
&& mv /usr/local/bin/ec-linux-amd64 /usr/local/bin/editorconfig-checker \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list > /dev/null \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
&& apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    nomad=1.4.4-1 \
    /tmp/oasdiff.deb \
&& curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
&& pyenv install 3.11.2 \
&& pyenv install 3.9.16 \
&& rm -rf /var/lib/apt/lists/* /tmp/oasdiff.deb \
&& pyenv global 3.11.2 3.9.16
COPY --from=golang:1.18.3 /usr/local/go/ /usr/local/go/

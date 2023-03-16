# python:3.11.2-slim-bullseye
ARG REGISTRY
FROM ${REGISTRY}python@sha256:f776eb0acc768c0227cd336e33a97f3054101cf35ee6d5d8dc51b82349429925
ENV PATH=/usr/local/go/bin:$PATH
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    git \
    gnupg \
    jq \
    lsb-release \
    python3-distutils \
    ssh \
    unzip \
    wget \
    xz-utils \
&& curl -fsSL https://static.pantsbuild.org/setup/pantsup.sh | bash /dev/stdin --bin-dir /usr/local/bin --version 0.5.4 \
&& curl -fsSL https://github.com/Tufin/oasdiff/releases/download/v1.3.9/oasdiff_1.3.9_linux_amd64.deb > /tmp/oasdiff.deb \
&& curl -fsSL https://sentry.io/get-cli/ | SENTRY_CLI_VERSION=2.15.1 bash \
&& curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
&& curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
&& curl -sfSL https://github.com/editorconfig-checker/editorconfig-checker/releases/download/2.7.0/ec-linux-amd64.tar.gz | tar xvz -C /usr/local bin/ec-linux-amd64 \
&& mv /usr/local/bin/ec-linux-amd64 /usr/local/bin/editorconfig-checker \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list > /dev/null \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
&& apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    nomad=1.5.1-1 \
    /tmp/oasdiff.deb \
&& rm -rf /var/lib/apt/lists/* /tmp/oasdiff.deb
COPY --from=golang:1.19.7 /usr/local/go/ /usr/local/go/

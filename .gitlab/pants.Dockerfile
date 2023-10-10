# python:3.11.6-slim-bookworm
ARG REGISTRY
FROM ${REGISTRY}python@sha256:ad2c4e5884418404c5289acad4a471dde8500e24ba57ad574cdcae46523e507a
ENV PATH=/usr/local/go/bin:$PATH
COPY --from=golang:1.19.12-bullseye /usr/local/go/ /usr/local/go/
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
    expect \
&& curl -fsSL https://static.pantsbuild.org/setup/pantsup.sh | bash /dev/stdin --bin-dir /usr/local/bin --version 0.10.3 \
&& curl -fsSL https://github.com/Tufin/oasdiff/releases/download/v1.8.0/oasdiff_1.8.0_linux_amd64.deb > /tmp/oasdiff.deb \
&& curl -fsSL https://sentry.io/get-cli/ | SENTRY_CLI_VERSION=2.21.2 bash \
&& curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
&& curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
&& curl -fsSL https://raw.githubusercontent.com/ory/meta/master/install.sh | bash /dev/stdin -b ./usr/local/bin ory v0.2.2 \
&& curl -fsSL https://github.com/editorconfig-checker/editorconfig-checker/releases/download/2.7.1/ec-linux-amd64.tar.gz | tar xvz -C /usr/local bin/ec-linux-amd64 \
&& mv /usr/local/bin/ec-linux-amd64 /usr/local/bin/editorconfig-checker \
&& curl -sfSL https://github.com/orhun/git-cliff/releases/download/v1.3.1/git-cliff-1.3.1-x86_64-unknown-linux-gnu.tar.gz | tar xvz -C /usr/local git-cliff-1.3.1/git-cliff \
&& mv /usr/local/git-cliff-1.3.1/git-cliff /usr/local/bin/git-cliff \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list > /dev/null \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
&& apt-get update && apt-get install -y --no-install-recommends \
    consul-template=0.33.0-1 \
    docker-ce-cli \
    nomad=1.6.2-1 \
    /tmp/oasdiff.deb \
&& rm -rf /var/lib/apt/lists/* /tmp/oasdiff.deb \
&& printf "[GLOBAL]\npants_version = \"2.17.1rc0\"" > /tmp/pants.toml && cd /tmp/ && pants --version && rm /tmp/pants.toml

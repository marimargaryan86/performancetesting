ARG REGISTRY
FROM ${REGISTRY}python:3.11.8-slim-bookworm@sha256:6459da0f052d819e59b5329bb8f76b2f2bd16427ce6fd4db91e11b3759850380
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    expect \
    git \
    gnupg \
    jq \
    lsb-release \
    python3-distutils \
    ssh \
    unzip \
    wget \
    xz-utils \
    yq

# renovate: datasource=github-releases depName=hcl2json packageName=tmccombs/hcl2json
ENV HCL2JSON_VERSION=v0.6.3
RUN curl -fsSL https://github.com/tmccombs/hcl2json/releases/download/${HCL2JSON_VERSION}/hcl2json_linux_amd64 -o /usr/local/bin/hcl2json && chmod +x /usr/local/bin/hcl2json

# renovate: datasource=golang-version depName=go
ENV GO_VERSION=1.22.2
ENV PATH=/usr/local/go/bin:$PATH
RUN curl -fsSL https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz | tar xz -C /usr/local

# renovate: datasource=github-releases depName=scie-pants packageName=pantsbuild/scie-pants
ENV SCIE_PANTS_VERSION=v0.11.0
RUN curl -fsSL https://static.pantsbuild.org/setup/pantsup.sh | bash /dev/stdin --bin-dir /usr/local/bin --version ${SCIE_PANTS_VERSION:1}

# renovate: datasource=github-releases depName=oasdiff packageName=Tufin/oasdiff
ENV OASDIFF_VERSION=v1.10.15
RUN curl -fsSL https://github.com/Tufin/oasdiff/releases/download/${OASDIFF_VERSION}/oasdiff_${OASDIFF_VERSION:1}_linux_amd64.deb > /tmp/oasdiff.deb && \
    apt-get install -y --no-install-recommends /tmp/oasdiff.deb && \
    rm /tmp/oasdiff.deb

# renovate: datasource=github-releases depName=sentry-cli packageName=getsentry/sentry-cli
ENV SENTRY_CLI_VERSION=2.30.0
RUN curl -fsSL https://sentry.io/get-cli/ | bash

# renovate: datasource=github-releases depName=editorconfig-checker packageName=editorconfig-checker/editorconfig-checker
ENV EDITORCONFIG_CHECKER_VERSION=v3.0.1
RUN curl -fsSL https://github.com/editorconfig-checker/editorconfig-checker/releases/download/${EDITORCONFIG_CHECKER_VERSION}/ec-linux-amd64.tar.gz | tar xz -C /usr/local bin/ec-linux-amd64 && \
    mv /usr/local/bin/ec-linux-amd64 /usr/local/bin/editorconfig-checker

# renovate: datasource=github-releases depName=git-cliff packageName=orhun/git-cliff
ENV GIT_CLIFF_VERSION=v2.1.2
RUN curl -sfSL https://github.com/orhun/git-cliff/releases/download/${GIT_CLIFF_VERSION}/git-cliff-${GIT_CLIFF_VERSION:1}-x86_64-unknown-linux-gnu.tar.gz | tar xz -C /usr/local git-cliff-${GIT_CLIFF_VERSION:1}/git-cliff && \
    mv /usr/local/git-cliff-${GIT_CLIFF_VERSION:1}/git-cliff /usr/local/bin/git-cliff

# renovate: datasource=github-releases depName=consul-template packageName=hashicorp/consul-template
ENV CONSUL_TEMPLATE_VERSION=v0.37.5
# renovate: datasource=github-releases depName=nomad packageName=hashicorp/nomad
ENV NOMAD_VERSION=v1.7.7
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list > /dev/null && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && apt-get install -y --no-install-recommends \
        consul-template=${CONSUL_TEMPLATE_VERSION:1}-1 \
        docker-ce-cli \
        docker-buildx-plugin \
        nomad=${NOMAD_VERSION:1}-1 &&\
    rm -rf /var/lib/apt/lists/*

ARG PANTS_VERSION
RUN printf "[GLOBAL]\npants_version = \"${PANTS_VERSION}\"" > /tmp/pants.toml && \
    cd /tmp/ && pants --no-local-cache --no-pantsd --version && \
    rm /tmp/pants.toml

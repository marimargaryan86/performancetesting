ARG REGISTRY
# 3.11.6-slim-bookworm
FROM ${REGISTRY}python@sha256:38a28170d13a276d42b7dd55cae54440b581d773549d361d19089ec47d4791c5
ENV PATH=/usr/local/go/bin:$PATH
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
&& curl -fsSL https://go.dev/dl/go1.19.13.linux-amd64.tar.gz | tar xz -C /usr/local \
&& curl -fsSL https://static.pantsbuild.org/setup/pantsup.sh | bash /dev/stdin --bin-dir /usr/local/bin --version 0.10.4 \
&& curl -fsSL https://github.com/Tufin/oasdiff/releases/download/v1.10.0/oasdiff_1.10.0_linux_amd64.deb > /tmp/oasdiff.deb \
&& curl -fsSL https://sentry.io/get-cli/ | SENTRY_CLI_VERSION=2.22.3 bash \
&& curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
&& curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
&& curl -fsSL https://github.com/editorconfig-checker/editorconfig-checker/releases/download/2.7.2/ec-linux-amd64.tar.gz | tar xz -C /usr/local bin/ec-linux-amd64 \
&& mv /usr/local/bin/ec-linux-amd64 /usr/local/bin/editorconfig-checker \
&& curl -sfSL https://github.com/orhun/git-cliff/releases/download/v1.4.0/git-cliff-1.4.0-x86_64-unknown-linux-gnu.tar.gz | tar xz -C /usr/local git-cliff-1.4.0/git-cliff \
&& mv /usr/local/git-cliff-1.4.0/git-cliff /usr/local/bin/git-cliff \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list > /dev/null \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
&& apt-get update && apt-get install -y --no-install-recommends \
    consul-template=0.35.0-1 \
    docker-ce-cli \
    nomad=1.6.3-1 \
    /tmp/oasdiff.deb \
&& rm -rf /var/lib/apt/lists/* /tmp/oasdiff.deb \
&& printf "[GLOBAL]\npants_version = \"2.20.0.dev1\"" > /tmp/pants.toml && cd /tmp/ && pants --no-local-cache --no-pantsd --version && rm /tmp/pants.toml

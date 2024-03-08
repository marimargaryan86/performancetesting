ARG REGISTRY
# 3.11.8-slim-bookworm
FROM ${REGISTRY}python@sha256:6459da0f052d819e59b5329bb8f76b2f2bd16427ce6fd4db91e11b3759850380
ENV PATH=/usr/local/go/bin:$PATH
ARG PANTS_VERSION
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
&& curl -fsSL https://github.com/tmccombs/hcl2json/releases/download/v0.6.1/hcl2json_linux_amd64 -o /usr/local/bin/hcl2json \
&& chmod +x /usr/local/bin/hcl2json \
&& curl -fsSL https://go.dev/dl/go1.19.13.linux-amd64.tar.gz | tar xz -C /usr/local \
&& curl -fsSL https://static.pantsbuild.org/setup/pantsup.sh | bash /dev/stdin --bin-dir /usr/local/bin --version 0.10.7 \
&& curl -fsSL https://github.com/Tufin/oasdiff/releases/download/v1.10.11/oasdiff_1.10.11_linux_amd64.deb > /tmp/oasdiff.deb \
&& curl -fsSL https://sentry.io/get-cli/ | SENTRY_CLI_VERSION=2.30.0 bash \
&& curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
&& curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
&& curl -fsSL https://github.com/editorconfig-checker/editorconfig-checker/releases/download/v3.0.0/ec-linux-amd64.tar.gz | tar xz -C /usr/local bin/ec-linux-amd64 \
&& mv /usr/local/bin/ec-linux-amd64 /usr/local/bin/editorconfig-checker \
&& curl -sfSL https://github.com/orhun/git-cliff/releases/download/v2.1.2/git-cliff-2.1.2-x86_64-unknown-linux-gnu.tar.gz | tar xz -C /usr/local git-cliff-2.1.2/git-cliff \
&& mv /usr/local/git-cliff-2.1.2/git-cliff /usr/local/bin/git-cliff \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list > /dev/null \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
&& apt-get update && apt-get install -y --no-install-recommends \
    consul-template=0.37.1-1 \
    docker-ce-cli \
    docker-buildx-plugin \
    nomad=1.7.5-1 \
    /tmp/oasdiff.deb \
&& rm -rf /var/lib/apt/lists/* /tmp/oasdiff.deb \
&& printf "[GLOBAL]\npants_version = \"${PANTS_VERSION}\"" > /tmp/pants.toml && cd /tmp/ && pants --no-local-cache --no-pantsd --version && rm /tmp/pants.toml

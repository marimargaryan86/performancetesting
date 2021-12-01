FROM python:3.9.9
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    jq \
    lsb-release \
&& curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
&& apt-get update && apt-get install -y \
    docker-ce-cli \
&& rm -rf /var/lib/apt/lists/*
COPY --from=golang:1.17.3 /usr/local/go/ /usr/local/go/
ENV PATH=$PATH:/usr/local/go/bin

FROM python:3.9.7
COPY --from=golang:1.16.9 /usr/local/go/ /usr/local/go/
ENV PATH=$PATH:/usr/local/go/bin

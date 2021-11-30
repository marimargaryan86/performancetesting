FROM python:3.9.9
COPY --from=golang:1.17.3 /usr/local/go/ /usr/local/go/
ENV PATH=$PATH:/usr/local/go/bin

from enum import Enum


class RequestType(Enum):
    post = "POST"
    get = "GET"
    put = "PUT"
    delete = "DELETE"


class Format(Enum):
    application_pdf = "application/pdf"
    image_png = "image/png"

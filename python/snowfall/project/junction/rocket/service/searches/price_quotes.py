import pymongo

from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import repository


class QuoteRepository(repository.ProtoRepository[models_pb2.Quote]):
    _proto = models_pb2.Quote
    _indexes = (pymongo.IndexModel("quotes._id", background=True),)

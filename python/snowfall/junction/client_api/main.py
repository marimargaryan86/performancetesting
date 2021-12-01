from starlette import applications, exceptions

from snowfall.junction.client_api import handlers

app = applications.Starlette()
app.add_exception_handler(exceptions.HTTPException, handlers.exception_handler)

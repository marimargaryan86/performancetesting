from starlette import endpoints, requests, responses, status


class IncomingMessages(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
    ) -> responses.Response:
        await request.form()
        # Context Manager for now can be a function under this service, eventually
        # we could make it grpc methods under notification_center service
        # response = context_manager.create_response(  # Here we get also the state
        # This could be inside the context_manager as a call. Just showing it here

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

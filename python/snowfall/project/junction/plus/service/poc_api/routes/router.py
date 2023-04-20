import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.plus.service.poc_api.routes import chatbot, register


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    return [
        integration.route("/whatsapp", chatbot.Whatsapp),
        integration.route("/register", register.WhatsappRegister),
        integration.route("/subscribers", register.WhatsappSubscriberRegister),
        integration.route("/journey-delays", register.WebhookDelay),
    ]

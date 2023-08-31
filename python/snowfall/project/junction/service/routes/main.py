from snowfall.project.junction.service.routes import factories
from snowfall.stdlib.service import application

if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="routes")

    entrypoint.enter_with_commands(
        application.Command(
            name="import-nodes",
            callback=factories.import_nodes,
            settings_class=factories.ImportSettings,
        ),
    )

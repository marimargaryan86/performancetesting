from snowfall.project.junction.service.providers.benerail import config, stations
from snowfall.stdlib import service

if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="benerail")

    entrypoint.enter_with_commands(
        service.Command(
            name="dump-stations",
            callback=stations.dump_stations,  # type: ignore[attr-defined]
            settings_class=config.DumpStationsSettings,
        ),
    )

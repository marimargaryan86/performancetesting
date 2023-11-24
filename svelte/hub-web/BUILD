files(sources=["**/*"], name="files")

relocated_files(
    name="relocated_files",
    files_targets=[":files"],
    src="svelte/hub-web",
    dest="",
)

custom_image(
    prefix="junction-hub",
    name="docker",
    dependencies=[":relocated_files"],
)

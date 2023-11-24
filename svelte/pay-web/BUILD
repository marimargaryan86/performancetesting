files(sources=["**/*"], name="files")

relocated_files(
    name="relocated_files",
    files_targets=[":files"],
    src="svelte/pay-web",
    dest="",
)

custom_image(
    prefix="pay",
    name="docker",
    dependencies=[":relocated_files"],
)

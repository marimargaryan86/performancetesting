files(sources=["**/*"], name="files")

relocated_files(
    name="relocated_files",
    files_targets=[":files"],
    src="svelte/hub-web",
    dest="",
)

docker_image(
    name="docker",
    dependencies=[":relocated_files"],
    image_tags=["{build_args.VERSION}"],
)

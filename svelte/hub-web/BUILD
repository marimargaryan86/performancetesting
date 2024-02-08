files(sources=["**/*"], name="files")

custom_image(
    prefix="junction-hub",
    name="docker",
    dependencies=[":files", "//svelte:files"],
)

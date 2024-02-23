import subprocess  # noqa: S404


def compile_translation() -> None:
    command = ["pybabel", "compile", "-d", "translations"]
    subprocess.run(command, check=True)  # noqa: S603


if __name__ == "__main__":
    compile_translation()

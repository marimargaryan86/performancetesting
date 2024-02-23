files(
    name="translations_es",
    sources=["es/LC_MESSAGES/messages.po"],
)

files(
    name="translations_eng",
    sources=["eng/LC_MESSAGES/messages.po"],
)

pex_binary(
    name="pybabel",
    script="pybabel",
    dependencies=["vendor#Babel"],
)

adhoc_tool(
    name="compile_translations",
    runnable=":pybabel",
    args=["compile", "-d", "."],
    execution_dependencies=[
        ":translations_eng",
        ":translations_es",
    ],
    output_directories=["."],
)

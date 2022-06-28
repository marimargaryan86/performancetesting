export default (input, _, context) => {
    if (input.summary === undefined) {
        return
    }

    const firstWord = input.summary.split(' ')[0]

    if (firstWord !== "List") {
        return
    }

    const cursorError = {
        message: `${context.path.join('.')} - "List" endpoint is missing "page[cursor]" parameter`,
    }
    const limitError = {
        message: `${context.path.join('.')} - "List" endpoint is missing "page[limit]" parameter`,
    }

    if (input.parameters === undefined) {
        return [cursorError, limitError]
    }

    let errors = []

    if (input.parameters.filter(e => e.name === "page[cursor]").length === 0) {
        errors.push(cursorError)
    }

    if (input.parameters.filter(e => e.name === "page[limit]").length === 0) {
        errors.push(limitError)
    }

    return errors
}

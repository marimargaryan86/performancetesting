let ensureRefs = (input, _, context) => {
    let dataValues = []
    let errors = []

    if (input.hasOwnProperty("items")) {
        if (input.items.hasOwnProperty("oneOf")) {
            for (const oneOf of input.items.oneOf) {
                errors.concat(ensureRefs(oneOf, _, context))
            }

            return errors
        }

        dataValues.push(input.items)
    } else if (input.hasOwnProperty("oneOf")) {
        for (const oneOf of input.oneOf) {
            errors.concat(ensureRefs(oneOf, _, context))
        }

        return errors
    } else {
        dataValues.push(input)
    }

    for (const dataValue of dataValues) {
        if (!dataValue.hasOwnProperty("$ref")) {
            errors.push({
                message: `Resource data field is not a $ref`,
            })
        }
    }

    return errors
}

export default ensureRefs

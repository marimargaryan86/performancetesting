const flattenResource = (input) => {
    let resource

    if (input.hasOwnProperty("items")) {
        return flattenResource(input.items)
    }

    if (input.hasOwnProperty("allOf")) {
        resource = getKeyInAllOf(input.allOf).flatMap(({ properties }) => properties)[0]
    } else {
        resource = input.properties
    }

    return resource
}

const getKeyInAllOf = (allOf) => {
    return allOf.flatMap(
        (item) => {
            if (item.hasOwnProperty("allOf")) {
                return getKeyInAllOf(item.allOf)
            }

            return item
        }
    )
}

let ensureRequiredFields = (input, options, context) => {
    if (options.required === undefined) {
        return
    }

    if (input === undefined) {
        input = {}
    }

    let resource = flattenResource(input)
    let errors = []

    if (input.hasOwnProperty("oneOf")) {
        for (const oneOf of input.oneOf) {
            errors.concat(ensureRequiredFields(oneOf, options, context))
        }

        return errors
    } else if (resource.hasOwnProperty("items")) {
        resource = flattenResource(resource.items)
    }

    for (const required of options.required) {
        if (!resource.hasOwnProperty(required)) {
            errors.push({
                message: `Required field ${required} is missing at ${context.path.join('.')}`,
            })
        }
    }

    return errors
}

export default ensureRequiredFields

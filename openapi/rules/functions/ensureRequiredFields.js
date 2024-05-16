const checkRequiredFields = (input, options, context, path) => {
    if (Object.hasOwn(input, "type") && input.type != "object") {
      return []
    }

    if (!Object.hasOwn(input, "properties")) {
      return []
    }

    const properties = Object.keys(input.properties)
    let required = []

    if (Object.hasOwn(input, "required")) {
      required = input.required
    }

    const difference = properties.filter(x => !required.includes(x));
    let errors = []

    if (difference.length > 0) {
      for (const diff of difference) {
        if (diff === "included") continue
        errors.push({
          message: `Property '${diff}' is not marked as required`,
          path: [...path]
        })
      }
    }

    for (const property of properties) {
      errors = errors.concat(checkRequiredFields(input.properties[property], options, context, [...path, "properties", property]))
    }

    return errors
}

const ensureRequiredFields = (input, options, context) => {
  let errors = []

  for (const contentType of Object.keys(input)) {
    if (!contentType.includes("json")) {
      return
    }

    errors = errors.concat(checkRequiredFields(input[contentType].schema, options, context, [...context.path, contentType, "schema"]))
  }

  return errors
}

export default ensureRequiredFields

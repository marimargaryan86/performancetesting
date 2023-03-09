export default (input, options, context) => {
  if (options.required === undefined) {
    return
  }

  let errors = []

  for (const required of options.required) {
    if (!input.includes(required)) {
      errors.push({
          message: `Field "${required}" must be required.`,
      })
    }
  }

  return errors
}

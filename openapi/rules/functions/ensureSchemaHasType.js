export default (input, _, context) => {
  if (input.oneOf || input.type || input['$ref']) {
    return
  }

  return [{
    message: `${context.path ? context.path.join('.') : 'type or $ref'} is not truthy`,
  }]
};

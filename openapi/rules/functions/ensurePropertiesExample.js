export default (input, _, context) => {
  if (
      context.path.join('.').includes('properties.properties') ||
      // skip if this is an example
      context.path.includes('example') ||
      // objects are not basic values
      input.type === 'object' ||
      // binary values are not basic values
      input.format === 'binary' ||
      // arrays can be skipped unless they are string arrays
      (input.type === 'array' && input.items && input.items.type !== 'string') ||
      // skip if the property as a reference
      input['$ref'] !== undefined ||
      input.allOf !== undefined ||
      // if this is a list
      input.oneOf !== undefined ||
      // allow an explicit example value of null
      input.example === null ) { return }

  // if the item does not have an example
  // throw an error
  if (!input.example && input.example !== false) {
    return [
      {
        message: `${context.path ? context.path.join('.') : 'property'} is not truthy`,
      }
    ]
  }
}

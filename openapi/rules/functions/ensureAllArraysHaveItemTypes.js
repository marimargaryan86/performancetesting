export default (input, _, context) => {
  // if this is actually a property called properties, ignore
  if (context.path.join('.').includes('properties.properties')) { return }

  // if this is a list, check if the first item matches instead
  if (input.items && input.items.oneOf) { return }

  // check if the param is an array
  if (input.type === 'array' &&
    // if the param has items, ensure it has a type or a ref
    !(input.items && (input.items.type || input.items['$ref']))) {
    return [
      {
        message: `All properties and params of type array need an item type or $ref`
      }
    ]
  }
}

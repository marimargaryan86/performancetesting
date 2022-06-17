export default (input, _, context) => {
  // get the keys for an item
  let keys = input.map(row => Object.keys(row)[0])

  // if the item contains a reference, ensure it's
  // the first item
  if (keys.includes("$ref") && keys[0] !== "$ref") {
    return [
      {
        message: `$ref needs to be first item in allOf set`
      }
    ]
  }

  // if the item contains a reference, ensure the description is
  // the second item, unless the second option is a direct
  // list of properties
  if (keys.includes("$ref") && keys[1] && keys[1] !== "description" && keys[1] !== "properties") {
    return [
      {
        message: `description or properties needs to be second item in allOf set`
      }
    ]
  }

  // Check of there are any keys we did not expect
  let excessKeys = keys && ["$ref", "description"]
  if (keys["$ref"] && excessKeys.length > 0) {
    return [
      {
        message: `Unexpected items under allOf: ${excessKeys}`
      }
    ]
  }
}

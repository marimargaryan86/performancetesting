export default (input, _, context) => {
  let given = context.path
  // remove the first element from the path
  given.shift()
  // create the expected ID
  const id = given.reverse()
                  .join('')
                  .replace(/\//g, '-')
                  .replace(/{[A-Za-z-]*}/g, 'id')
                  .replace(/\.id/g, '-id')

  // check the expected ID against the operationId
  if (id != input.operationId) {
    return [{ message: `Expected operationId to equal ${id}`}]
  }
}

export default (input, _, context) => {
  if (input.summary === undefined || input.operationId === undefined) {
    return
  }

  const firstWord = input.summary.split(' ')[0]
  const verb = input.operationId.split('-')[0]
  const endWithId = input.operationId.endsWith('-id')
  const endsWithS = input.operationId.endsWith('s')
  const endsWithStatus = input.operationId.endsWith('status')

  // When getting an item by ID, use "Get"
  if (verb === 'get' && (endWithId || endsWithStatus) && firstWord !== 'Get') {
    return [
      {
        message: `${context.path.join('.')} - summary should start with "Get"`,
      }
    ]
  }
  // When getting all items, try to use "List" and reject "Get"
  else if (verb === 'get' && !(endWithId || endsWithStatus) && endsWithS && firstWord === 'Get') {
    return [
      {
        message: `${context.path.join('.')} - summary should not start with "Get". Please use "List" where possible.`,
      }
    ]
  }
  // When deleting items, ensure we use "Delete" or "Remove" or "Permanently remove", or "Unassign"
  else if (verb === 'delete' && !(input.summary.startsWith('Delete') || input.summary.startsWith('Remove') || input.summary.startsWith('Permanently remove') || input.summary.startsWith('Unassign'))) {
    return [
      {
        message: `${context.path.join('.')} - summary should start with "Delete" or "Remove" or "Permanently remove" or "Unassign".`,
      }
    ]
  }
  // When creating items, ensure we use "Create" or "Assign" or "Add"
  else if (verb === 'post' && endsWithS && !endWithId && !(input.summary.startsWith('Create') || input.summary.startsWith('Assign')  || input.summary.startsWith('Add'))) {
    return [
      {
        message: `${context.path.join('.')} - summary should start with "Create" or "Assign" or "Add".`,
      }
    ]
  }
  // When updating items, ensure we use "Update" or "Transfer" por "Upload"
  else if (verb === 'patch' && endWithId && !(input.summary.startsWith('Update') || input.summary.startsWith('Transfer') || input.summary.startsWith('Upload'))) {
    return [
      {
        message: `${context.path.join('.')} - summary should start with "Update" or "Transfer" or "Upload".`,
      }
    ]
  }
}

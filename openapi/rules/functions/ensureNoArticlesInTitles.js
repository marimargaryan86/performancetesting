export default (input, _, context) => {
  if (input.summary === undefined) {
    return
  }

  if (input.summary.includes(' a ') || input.summary.includes(' an ') || input.summary.includes(' the ')) {
    return [
      {
        message: `${context.path.join('.')} - summary should not include "a", "an" or "the"`,
      }
    ]
  }
}

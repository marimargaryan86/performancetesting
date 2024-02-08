/** @type {import("prettier").Config} */
module.exports = {
  useTabs: false,
  singleQuote: false,
  trailingComma: "all",
  printWidth: 100,
  plugins: ["prettier-plugin-svelte"],
  overrides: [
    {
      files: "*.svelte",
      options: {
        parser: "svelte",
      },
    },
  ],
  svelteSortOrder: "scripts-options-markup-styles",
  bracketSameLine: false,
};

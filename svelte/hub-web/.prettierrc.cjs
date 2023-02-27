module.exports = {
  useTabs: false,
  singleQuote: false,
  trailingComma: "all",
  printWidth: 100,
  plugins: ["prettier-plugin-svelte"],
  pluginSearchDirs: ["."],
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

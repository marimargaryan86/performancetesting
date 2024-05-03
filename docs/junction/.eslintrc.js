module.exports = {
    env: {
        browser: true,
        es2021: true
    },
    extends: [
        "standard-with-typescript",
        "plugin:@docusaurus/recommended",
        "plugin:react/recommended",
    ],
    parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        project: './tsconfig.eslint.json'
    },
    plugins: [
        "react"
    ],
    ignorePatterns: [
        "openapi/**",
        ".eslintrc.js",
        "src/components/Button.js",
        "src/components/Dots.js",
        "src/components/HeaderMenu.js",
        "src/pages/index.js"
    ],
    rules: {
        "@typescript-eslint/naming-convention": "off",
        "@typescript-eslint/no-var-requires": "off"
    },
    settings: {
        react: {
            version: "detect"
        }
    }
};

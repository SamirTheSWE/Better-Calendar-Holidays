const angular = require("@angular-eslint/eslint-plugin");
const angularTemplate = require("@angular-eslint/eslint-plugin-template");
const angularTemplateParser = require("@angular-eslint/template-parser");
const tsEslint = require("@typescript-eslint/eslint-plugin");
const tsParser = require("@typescript-eslint/parser");

module.exports = [
    {
        files: ["**/*.ts"],
        ignores: ["dist/**", "node_modules/**"],
        languageOptions: {
            parser: tsParser,
            parserOptions: {
                project: ["./tsconfig.app.json"],
            },
        },
        plugins: {
            "@angular-eslint": angular,
            "@typescript-eslint": tsEslint,
        },
        rules: {
            ...tsEslint.configs.recommended.rules,
            ...angular.configs.recommended.rules,
            "@angular-eslint/component-class-suffix": "error",
            "@angular-eslint/directive-class-suffix": "error",
        },
    },
    {
        files: ["**/*.html"],
        ignores: ["dist/**", "node_modules/**"],
        languageOptions: {
            parser: angularTemplateParser,
        },
        plugins: {
            "@angular-eslint/template": angularTemplate,
        },
        rules: {
            ...angularTemplate.configs.recommended.rules,
        },
    },
];

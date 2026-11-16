## Repository

- Public, MIT License
- Website: https://eslint-react.xyz/docs
- Stars: 594 · Watchers: 2 · Forks: 61
- Default branch: main · Releases: 491 · Tags: 504
- Created: 2023-08-18

[![logo](https://camo.githubusercontent.com/403b3cea34241f599a63b76387f4df0d4960a9e185171e753c01c09b59e6b1e1/68747470733a2f2f65736c696e742d72656163742e78797a2f6c6f676f2e737667)](https://camo.githubusercontent.com/403b3cea34241f599a63b76387f4df0d4960a9e185171e753c01c09b59e6b1e1/68747470733a2f2f65736c696e742d72656163742e78797a2f6c6f676f2e737667)

# ESLint React

[![Version](https://camo.githubusercontent.com/9c878ecc3be21bee49833cbae3263df11b47f5d5585b32993fa59a36499e4b01/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f762f65736c696e742d706c7567696e2d72656163742d783f7374796c653d666c617426636f6c6f72413d31313131313126636f6c6f72423d303030303030)](https://npmx.dev/package/eslint-plugin-react-x) [![Downloads](https://camo.githubusercontent.com/dbca38e3b4e267a48958a140212a28c180567211cf4a07237e512a9cc1b5ca0e/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f64742f65736c696e742d706c7567696e2d72656163742d782e7376673f7374796c653d666c617426636f6c6f72413d32323232323226636f6c6f72423d303030303030)](https://npmx.dev/package/eslint-plugin-react-x) [![License](https://camo.githubusercontent.com/fd6eaf06ea5b727abf3c50ae395caf4449673c67b55f4395b68f3b9ccb064bc4/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f6c2f65736c696e742d706c7567696e2d72656163742d783f7374796c653d666c617426636f6c6f72413d33333333333326636f6c6f72423d303030303030)](https://github.com/Rel1cx/eslint-react/blob/main/LICENSE) [![Build with](https://camo.githubusercontent.com/0b6a938ded19c454c0f9585a3850474ca2d808c040ed85ca4775c98a18e5ac7e/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6275696c745f776974682d7473646f776e40302e32332e312d3030303030303f7374796c653d666c6174)](https://tsdown.dev)

Composable ESLint rules for React and friends.

## Table of Contents

- Table of Contents
- Features
- Public Packages
  - Modular ESLint Plugins
  - Unified ESLint Plugin
- Installation
  - Install
  - Setup
- Presets
  - Bare Bones
  - General Purpose
  - TypeScript Specialized
  - Other
- Rules
- FAQ
- Migration
- Changelog
- Disclaimer
- Sponsors
- Contributing
- License

## Features

- **Modern**: First-class support for **TypeScript**, **React 19**, and more.
- **Flexible**: Fully customizable rule severity levels, allowing you to **enforce** or **relax** rules as needed.
- **Performant**: Built with performance in mind, optimized for large codebases, code editor responsiveness, and CI pipelines.
- **Context-aware linting**: Rules that understand the context of your code and [project configuration](https://eslint-react.xyz/docs/configuration/configure-project-config) to provide more **accurate** linting.

## Public Packages

### Modular ESLint Plugins

- [`eslint-plugin-react-x`](https://npmx.dev/package/eslint-plugin-react-x) - X rules (renderer-agnostic, compatible with x-platform).
- [`eslint-plugin-react-jsx`](https://npmx.dev/package/eslint-plugin-react-jsx) - React Flavored JSX rules.
- [`eslint-plugin-react-rsc`](https://npmx.dev/package/eslint-plugin-react-rsc) - Rules for React Server Components.
- [`eslint-plugin-react-dom`](https://npmx.dev/package/eslint-plugin-react-dom) - DOM-specific rules for React DOM.
- [`eslint-plugin-react-web-api`](https://npmx.dev/package/eslint-plugin-react-web-api) - Rules for interacting with Web APIs.
- [`eslint-plugin-react-naming-convention`](https://npmx.dev/package/eslint-plugin-react-naming-convention) - Naming convention rules.

### Unified ESLint Plugin

- [`@eslint-react/eslint-plugin`](https://npmx.dev/package/@eslint-react/eslint-plugin) - A unified plugin that combines all individual plugins into one. Get complete, out-of-the-box rule coverage with instant feedback.
Note

Don't know which one to use? See our [FAQ](https://eslint-react.xyz/docs/faq#which-one-should-i-use-unified-plugin-or-individual-plugins) for guidance.

## Installation

Note

ESLint React requires the following minimum versions:

- Node.js: 20.19.0
- ESLint: 10.0.0
- TypeScript: 5.0.0

### Install

```
npm install --save-dev typescript-eslint @eslint-react/eslint-plugin
```

### Setup

```
// eslint.config.js

import eslintReact from "@eslint-react/eslint-plugin";
import eslintJs from "@eslint/js";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";

export default defineConfig(
  {
    files: ["**/*.ts", "**/*.tsx"],

    // Extend recommended rule sets from:
    // 1. ESLint JS's recommended rules
    // 2. TypeScript ESLint recommended rules
    // 3. ESLint React's recommended-typescript rules
    extends: [
      eslintJs.configs.recommended,
      tseslint.configs.recommended,
      eslintReact.configs["recommended-typescript"],
    ],

    // Configure language/parsing options
    languageOptions: {
      // Use TypeScript ESLint parser for TypeScript files
      parser: tseslint.parser,
      parserOptions: {
        // Enable project service for better TypeScript integration
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },

    // Custom rule overrides (modify rule levels or disable rules)
    rules: {
      "@eslint-react/no-missing-key": "warn",
    },
  },
);
```

[Full Installation Guide ↗](https://eslint-react.xyz/docs/getting-started/typescript)

## Presets

### Bare Bones

- `x`
 Enable rules for React.
- `jsx`
 Enable rules for React Flavored JSX.
- `rsc`
 Enable rules for React Server Components.
- `dom`
 Enable rules for React DOM.
- `web-api`
 Enable rules for interacting with Web APIs.
- `naming-convention`
 Enable rules for naming conventions.

### General Purpose

- `recommended`
 Enforce rules that are recommended by ESLint React for general-purpose React + React DOM projects.
*This preset includes the `x`, `jsx`, `rsc`, `dom`, `web-api`, and `naming-convention` presets.*
- `strict`
 Same as the `recommended` preset but enables additional strict rules.

### TypeScript Specialized

- `recommended-typescript`
 Same as the `recommended` preset but disables rules that can be enforced by TypeScript.
- `recommended-type-checked`
 Same as the `recommended-typescript` preset but enables additional rules that require type information.
- `strict-typescript`
 Same as the `strict` preset but disables rules that can be enforced by TypeScript.
- `strict-type-checked`
 Same as the `strict-typescript` preset but enables additional rules that require type information.

### Other

- `disable-jsx`
 Disable rules in the `jsx` preset.
- `disable-rsc`
 Disable rules in the `rsc` preset.
- `disable-dom`
 Disable rules in the `dom` preset.
- `disable-web-api`
 Disable rules in the `web-api` preset.
- `disable-naming-convention`
 Disable rules in the `naming-convention` preset.
- `disable-experimental`
 Disable rules that have an "🧪 Experimental" feature flag.
- `disable-type-checked`
 Disable rules that require type information.
- `disable-conflict-eslint-plugin-react`
 Disable rules in `eslint-plugin-react` that conflict with rules in our plugins.
- `disable-conflict-eslint-plugin-react-hooks`
 Disable rules in `eslint-plugin-react-hooks` that conflict with rules in our plugins.
- `off`
 Disable all rules in this plugin.
[Full Presets List ↗](https://eslint-react.xyz/docs/presets)

## Rules

[Rules ↗](https://eslint-react.xyz/docs/rules)

## FAQ

[Frequently Asked Questions ↗](https://eslint-react.xyz/docs/faq)

## Migration

- [Migrating from eslint-plugin-react ↗](https://eslint-react.xyz/docs/migrating-from-eslint-plugin-react)
- [Migrating from eslint-plugin-react-hooks ↗](https://eslint-react.xyz/docs/migrating-from-eslint-plugin-react-hooks)

## Changelog

[Changelog ↗](https://eslint-react.xyz/docs/changelog)

## Disclaimer

This project is not affiliated with Meta Platforms, Inc. or the [react/react](https://github.com/react/react) project or team, nor is it endorsed or sponsored by them.

This project is, and will remain, [90% of its code written by humans](https://eslint-react.xyz/docs/faq#what-does-90-human-written-mean).

## Sponsors

A huge thank you to our amazing sponsors who make this project possible.

[ ![sponsors](https://camo.githubusercontent.com/38ab73dd491d48bfabfb990c52b8b723c2d82027844f9e2c0c8c284b90b5e0d9/68747470733a2f2f65736c696e742d72656163742e78797a2f73706f6e736f72732e737667) ](https://ko-fi.com/Rel1cx)

## Contributing

Contributions are welcome!

This project does not have contributing guidelines. Explore the repository to learn how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](/Rel1cx/eslint-react/blob/main/LICENSE) file for details.

## Files

.github/, .pkgs/, .zed/, apps/, docs/, examples/, packages/, patches/, plugins/, scripts/, testing/samples/, .editorconfig, .gitattributes, .gitignore, .mdxlintrc.json, .npmrc, .tazerc.json, .textlintrc.cjs, CHANGELOG.md, LICENSE, README.md, SECURITY.md, THIRD-PARTY-LICENSE, VERSION, assets, dprint.json, eslint.config.ts, nx.json, package.json, pnpm-lock.yaml, pnpm-workspace.yaml, tsconfig.json, tsl.config.ts, vitest.config.ts
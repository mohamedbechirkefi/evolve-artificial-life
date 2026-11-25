<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Generated from installed metadata in the M6 session: Python from the locked `.venv` (`importlib.metadata`: `License-Expression`, else the licence classifiers), npm from `demo/node_modules/*/package.json` for every entry of `demo/package-lock.json`. Accepted as permissive: MIT, BSD, ISC, Apache-2.0, PSF-style, MPL-2.0, 0BSD, Zlib, CC0-1.0 and similar.

**Flags.** None. No dependency carries a copyleft licence stronger than MPL-2.0 (file-level copyleft), and no MPL-2.0 package is modified or shipped in source form by this repository: `hypothesis` is a test-only dependency, and the twelve MPL-2.0 npm packages are build-time CSS tooling (`lightningcss` and its platform binaries) whose code is not bundled into `demo/dist`. Notes: `matplotlib` uses its own PSF-based licence; `pillow` reports `MIT-CMU`; `numpy` bundles code under BSD-3-Clause, 0BSD, MIT, Zlib and CC0-1.0. All are permissive.

## Python (17 packages, `uv.lock`)

| Package | Version | Licence (as declared) | Role |
|---|---|---|---|
| contourpy | 1.4.0 | BSD-3-Clause | runtime (numpy, matplotlib and their dependencies) |
| cycler | 0.12.1 | BSD License | runtime (numpy, matplotlib and their dependencies) |
| fonttools | 4.68.0 | MIT | runtime (numpy, matplotlib and their dependencies) |
| hypothesis | 6.170.15 | MPL-2.0 | test (dev group) |
| iniconfig | 2.3.1 | MIT | test (dev group) |
| kiwisolver | 1.5.1 | BSD License | runtime (numpy, matplotlib and their dependencies) |
| matplotlib | 3.11.2 | Python Software Foundation License | runtime (numpy, matplotlib and their dependencies) |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime (numpy, matplotlib and their dependencies) |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | runtime (numpy, matplotlib and their dependencies) |
| pillow | 13.0.0 | MIT-CMU | runtime (numpy, matplotlib and their dependencies) |
| pluggy | 1.7.0 | MIT License | test (dev group) |
| Pygments | 2.21.0 | BSD-2-Clause | test (dev group) |
| pyparsing | 3.3.3 | MIT | runtime (numpy, matplotlib and their dependencies) |
| pytest | 9.2.0 | MIT | test (dev group) |
| python-dateutil | 4.0.0 | BSD-3-Clause | runtime (matplotlib dependency) |
| sortedcontainers | 2.4.0 | Apache Software License | test (dev group) |
| tzdata | 2026.6 | Apache-2.0 | runtime (matplotlib dependency) |

## npm (demo; 53 installed packages, 84 lockfile entries)

Runtime code shipped in `demo/dist`: `react`, `react-dom` and `scheduler` (all MIT). Everything else is build or test tooling.

| Package | Version | Licence | Role |
|---|---|---|---|
| @jridgewell/sourcemap-codec | 1.6.0 | MIT | dev (transitive) |
| @oxc-project/types | 0.156.0 | MIT | dev (transitive) |
| @rolldown/binding-darwin-arm64 | 1.2.19 | MIT | dev (transitive) |
| @rolldown/pluginutils | 1.1.1 | MIT | dev (transitive) |
| @standard-schema/spec | 1.1.0 | MIT | dev (transitive) |
| @types/chai | 5.2.3 | MIT | dev (transitive) |
| @types/deep-eql | 4.0.2 | MIT | dev (transitive) |
| @types/estree | 1.0.11 | MIT | dev (transitive) |
| @types/react | 19.3.0 | MIT | dev (direct) |
| @types/react-dom | 19.3.0 | MIT | dev (direct) |
| @vitejs/plugin-react | 6.1.2 | MIT | dev (direct) |
| @vitest/expect | 4.1.12 | MIT | dev (transitive) |
| @vitest/mocker | 4.1.12 | MIT | dev (transitive) |
| @vitest/pretty-format | 4.1.12 | MIT | dev (transitive) |
| @vitest/runner | 4.1.12 | MIT | dev (transitive) |
| @vitest/snapshot | 4.1.12 | MIT | dev (transitive) |
| @vitest/spy | 4.1.12 | MIT | dev (transitive) |
| @vitest/utils | 4.1.12 | MIT | dev (transitive) |
| assertion-error | 2.0.1 | MIT | dev (transitive) |
| chai | 6.3.0 | MIT | dev (transitive) |
| convert-source-map | 2.0.0 | MIT | dev (transitive) |
| csstype | 3.2.4 | MIT | dev (transitive) |
| detect-libc | 2.1.2 | Apache-2.0 | dev (transitive) |
| es-module-lexer | 2.3.2 | MIT | dev (transitive) |
| estree-walker | 3.0.3 | MIT | dev (transitive) |
| expect-type | 1.4.0 | Apache-2.0 | dev (transitive) |
| fdir | 6.5.0 | MIT | dev (transitive) |
| fsevents | 2.3.3 | MIT | dev (transitive) |
| lightningcss | 1.33.0 | MPL-2.0 | dev (transitive) |
| lightningcss-darwin-arm64 | 1.33.0 | MPL-2.0 | dev (transitive) |
| magic-string | 0.30.21 | MIT | dev (transitive) |
| nanoid | 3.3.20 | MIT | dev (transitive) |
| obug | 2.2.1 | MIT | dev (transitive) |
| pathe | 2.0.3 | MIT | dev (transitive) |
| picocolors | 1.1.1 | ISC | dev (transitive) |
| picomatch | 4.0.7 | MIT | dev (transitive) |
| postcss | 8.5.33 | MIT | dev (transitive) |
| react | 19.3.1 | MIT | runtime |
| react-dom | 19.3.1 | MIT | runtime |
| rolldown | 1.2.19 | MIT | dev (transitive) |
| scheduler | 0.28.0 | MIT | transitive |
| siginfo | 2.0.0 | ISC | dev (transitive) |
| source-map-js | 1.2.4 | BSD-3-Clause | dev (transitive) |
| stackback | 0.0.2 | MIT | dev (transitive) |
| std-env | 4.3.0 | MIT | dev (transitive) |
| tinybench | 2.9.0 | MIT | dev (transitive) |
| tinyexec | 1.4.0 | MIT | dev (transitive) |
| tinyglobby | 0.2.17 | MIT | dev (transitive) |
| tinyrainbow | 3.2.0 | MIT | dev (transitive) |
| typescript | 5.9.3 | Apache-2.0 | dev (direct) |
| vite | 8.3.5 | MIT | dev (direct) |
| vitest | 4.1.12 | MIT | dev (direct) |
| why-is-node-running | 2.3.0 | MIT | dev (transitive) |

Lockfile entries not installed on this machine (31; optional platform binaries for other operating systems, licence taken from the lockfile): @emnapi/core (MIT), @emnapi/runtime (MIT), @emnapi/wasi-threads (MIT), @napi-rs/wasm-runtime (MIT), @rolldown/binding-android-arm-eabi (MIT), @rolldown/binding-android-arm64 (MIT), @rolldown/binding-darwin-x64 (MIT), @rolldown/binding-freebsd-x64 (MIT), @rolldown/binding-linux-arm-gnueabihf (MIT), @rolldown/binding-linux-arm64-gnu (MIT), @rolldown/binding-linux-arm64-musl (MIT), @rolldown/binding-linux-ppc64-gnu (MIT), @rolldown/binding-linux-s390x-gnu (MIT), @rolldown/binding-linux-x64-gnu (MIT), @rolldown/binding-linux-x64-musl (MIT), @rolldown/binding-openharmony-arm64 (MIT), @rolldown/binding-wasm32-wasi (MIT), @rolldown/binding-win32-arm64-msvc (MIT), @rolldown/binding-win32-x64-msvc (MIT), @tybys/wasm-util (MIT), lightningcss-android-arm64 (MPL-2.0), lightningcss-darwin-x64 (MPL-2.0), lightningcss-freebsd-x64 (MPL-2.0), lightningcss-linux-arm-gnueabihf (MPL-2.0), lightningcss-linux-arm64-gnu (MPL-2.0), lightningcss-linux-arm64-musl (MPL-2.0), lightningcss-linux-x64-gnu (MPL-2.0), lightningcss-linux-x64-musl (MPL-2.0), lightningcss-win32-arm64-msvc (MPL-2.0), lightningcss-win32-x64-msvc (MPL-2.0), tslib (0BSD).

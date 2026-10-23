<div align="center">
  <a href="https://github.com/natify-sh">
    <img alt="natify-sh" src="https://raw.githubusercontent.com/natify-sh/.github/refs/heads/main/logo.svg" width="100" height="100"/>
  </a>
</div>

<div align="center">

# [natify-sh](https://github.com/natify-sh)

**Inter-language & build tools**

Inter-language integration with the thinnest native seams — CLI tools, CI automation & ports built with them.

[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7&style=flat-square)](https://stand-with-ukraine.pp.ua)

</div>

-----

## Projects

### Ahead-of-time compilation

#### [wasmext](https://github.com/natify-sh/py-wasmext)
![lang](https://img.shields.io/badge/Python-%233776AB?logo=python&logoColor=white)
![lang](https://img.shields.io/badge/C-%23A8B9CC?logo=c&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-%23008033)

Turns WebAssembly modules into **native CPython extensions**, in the manner of Cython. The `.wasm` is translated to C by `wasm2c` and compiled when the extension is built,
so the module runs without a WebAssembly engine, at the speed of compiled C. Exports become methods of an `Instance`, instances can be linked to each other without Python in between,
and WASI preview 1 is supported. Built extensions are tested on Linux, Windows, macOS, Pyodide and Android.

### Toolchain

#### [wabt-package](https://github.com/natify-sh/wabt-package)
![lang](https://img.shields.io/badge/Python-%233776AB?logo=python&logoColor=white)
![license](https://img.shields.io/github/license/natify-sh/wabt-package?color=%23008033)
[![release](https://img.shields.io/github/v/release/natify-sh/wabt-package?labelColor=%23181717&logo=github&logoColor=white)](https://github.com/natify-sh/wabt-package/releases/latest)

[WABT](https://github.com/WebAssembly/wabt), the WebAssembly Binary Toolkit, as a Python package: prebuilt `wat2wasm`, `wasm2c`, `wasm2wat` and the other tools, plus the `wasm2c` runtime and the simde headers for SIMD modules.
No WABT build needed. Wheels for Linux (glibc and musl), Windows and macOS. An unofficial redistribution.

#### [wasm-tools-package](https://github.com/natify-sh/wasm-tools-package)
![lang](https://img.shields.io/badge/Python-%233776AB?logo=python&logoColor=white)
![license](https://img.shields.io/github/license/natify-sh/wasm-tools-package?color=%23008033)
[![release](https://img.shields.io/github/v/release/natify-sh/wasm-tools-package?labelColor=%23181717&logo=github&logoColor=white)](https://github.com/natify-sh/wasm-tools-package/releases/latest)

[wasm-tools](https://github.com/bytecodealliance/wasm-tools), the Bytecode Alliance's WebAssembly toolkit, as a Python package: the prebuilt `wasm-tools` executable with all its subcommands
(`parse`, `print`, `validate`, `component`, `objdump`, `strip`, ...), plus a small `run()` wrapper for calling it from Python.
No Rust toolchain needed. Wheels for Linux (glibc and musl), Windows and macOS. An unofficial redistribution.

### Runtime

#### [wasmhost](https://github.com/natify-sh/py-wasmhost)
![lang](https://img.shields.io/badge/Python-%233776AB?logo=python&logoColor=white)
![webassembly](https://img.shields.io/badge/webassembly-%23654FF0?logo=webassembly&logoColor=white)
![license](https://img.shields.io/github/license/natify-sh/py-wasmhost?color=%23008033)
[![release](https://img.shields.io/github/v/release/natify-sh/py-wasmhost?labelColor=%23181717&logo=github&logoColor=white)](https://github.com/natify-sh/py-wasmhost/releases/latest)

WebAssembly from **CPython, PyPy and Pythonista**, with the JavaScript WebAssembly API: modules, instances, memory, globals and host functions. It runs on whichever backend is available:
JavaScriptCore (including a `JSContext` in Pythonista on iOS), Node or Bun, or, when installed, wasmtime or wasm3. Plain Python, no dependencies, no C extension of its own.

#### [fusedwasi](https://github.com/natify-sh/fusedwasi)
![lang](https://img.shields.io/badge/C-%23A8B9CC?logo=c&logoColor=white)
![lang](https://img.shields.io/badge/Python-%233776AB?logo=python&logoColor=white)
![license](https://img.shields.io/github/license/natify-sh/fusedwasi?color=%23008033)

Header-only **C host for the WASI Component Model**, for core modules fused from components (`wasm2c` and other C hosts), with a Python twin. It implements the flat core form of the `wasi:*` imports
and nothing else: no engine, no component parser. *Placeholder — nothing is released yet.*

-----

<div align="center">

[wabt-package](https://github.com/natify-sh/wabt-package) · [wasm-tools-package](https://github.com/natify-sh/wasm-tools-package) · [wasmext](https://github.com/natify-sh/py-wasmext) · [wasmhost](https://github.com/natify-sh/py-wasmhost) · [fusedwasi](https://github.com/natify-sh/fusedwasi)

</div>

<div align="center">
  <small>
    © 2026 <a href="https://github.com/natify-sh">natify-sh</a> · Ukraine 🇺🇦
  </small>
</div>

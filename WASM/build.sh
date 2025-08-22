
#!/bin/bash
set -e

emcc main.cpp -O3 \
  -s WASM=1 \
  -s MODULARIZE=1 \
  -s EXPORT_ES6=1 \
  -s EXPORT_NAME=Module \
  -s EXPORTED_FUNCTIONS="[ '_parse_nexrad', '_malloc', '_free']" \
  -s EXPORTED_RUNTIME_METHODS="['ccall','cwrap', 'HEAPU8']" \
  -s INITIAL_MEMORY=64MB -s MAXIMUM_MEMORY=1GB -s ALLOW_MEMORY_GROWTH=1 \
  -o module.js

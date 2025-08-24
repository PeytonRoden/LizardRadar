# === Paths ===
BZ2_ROOT   = $(HOME)/Documents/libs/bzip2
BZ2_INC    = $(BZ2_ROOT)
BZ2_LIB    = $(BZ2_ROOT)
STB_INC    = $(HOME)/Documents/libs/stb  # location of stb_image_write.h

# === Tools ===
CXX        = g++
EMCC       = emcc

# === Flags ===
CXXFLAGS   = -std=c++17 -Wall -O3 -I$(BZ2_INC) -I$(STB_INC)
CFLAGS     = -O3 -Wall -I$(BZ2_INC) -I$(STB_INC)
LDFLAGS    = -L$(BZ2_LIB) -lbz2

# SIMD for WebAssembly
EMCC_CXXFLAGS = $(CXXFLAGS) -msimd128
EMCC_CFLAGS   = $(CFLAGS)   -msimd128

# === Files ===
TARGET      = nexrad_parser
SRC_CPP     = main.cpp
BZ2_SOURCES_C = \
  $(BZ2_ROOT)/bzlib.c \
  $(BZ2_ROOT)/decompress.c \
  $(BZ2_ROOT)/crctable.c \
  $(BZ2_ROOT)/huffman.c \
  $(BZ2_ROOT)/randtable.c

WASM_TARGET = module.js

# === Emscripten linker flags ===
EMCC_LDFLAGS = \
  -s WASM=1 \
  -s MODULARIZE=1 \
  -s EXPORT_ES6=1 \
  -s EXPORT_NAME=Module \
  -s EXPORTED_FUNCTIONS="['_set_tilt_angles_index', '_get_tilt_angles_size', '_get_tilt_angles', '_set_selected_radar_moment', '_get_latitude_topleft', '_get_longitude_topleft', '_get_latitude_bottomright', '_get_longitude_bottomright', '_get_png_data', '_get_png_size', '_parse_nexrad', '_malloc', '_free']" \
  -s EXPORTED_RUNTIME_METHODS="['ccall','cwrap','HEAPU8','lengthBytesUTF8','stringToUTF8', 'HEAPF32']"\
  -s INITIAL_MEMORY=64MB \
  -s MAXIMUM_MEMORY=1GB \
  -s ALLOW_MEMORY_GROWTH=1

# === Rules ===
all: $(TARGET)

$(TARGET): $(SRC_CPP)
	$(CXX) $(CXXFLAGS) $(SRC_CPP) -o $(TARGET) $(LDFLAGS)

wasm:
	$(EMCC) $(EMCC_CFLAGS) -c $(BZ2_SOURCES_C)
	$(EMCC) $(EMCC_CXXFLAGS) -c $(SRC_CPP) -o main.o
	$(EMCC) *.o $(EMCC_LDFLAGS) -o $(WASM_TARGET)

clean:
	rm -f $(TARGET) $(WASM_TARGET) module.wasm *.o

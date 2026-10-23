#!/bin/sh
# Reviewed adaptation of official upstream build-linux-cpu+cuda.sh.
# GPU verified using nvidia-smi: RTX 3050 Ti Laptop, compute capability 8.6.
# CUDA 13.4 lists sm_86. GCC 16 is accepted by installed host_config.h.
# Preserve CPU executable; separate CUDA-enabled binary.
set -eu
cd "$(dirname "$0")/ebsynth"
exec /opt/cuda/bin/nvcc -arch=sm_86 -ccbin=/usr/bin/g++ \
  src/ebsynth.cpp src/ebsynth_cpu.cpp src/ebsynth_cuda.cu \
  -Iinclude -DNDEBUG -D__CORRECT_ISO_CPP11_MATH_H_PROTO \
  -O3 -std=c++11 -Xcompiler=-fopenmp -o bin/ebsynth-cuda

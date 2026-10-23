# Bounded CUDA build attempt

GPU readback from `nvidia-smi`: NVIDIA GeForce RTX 3050 Ti Laptop GPU, compute capability 8.6. CUDA compiler 13.4.92 explicitly lists `sm_86`. `nvcc --help` supports the selected architecture shorthand, explicit host compiler, and C++11. GCC 16.2.1 is present; GCC 14/15 binaries were unavailable. Installed CUDA host configuration does not reject GCC 16. Clang 23.1.1 is also present; it was not selected.

The reviewed local script `build-linux-cuda-sm86.sh` preserves upstream source and build scripts. Compared with upstream, it selects `sm_86`, explicitly uses `/usr/bin/g++`, changes optimization to `-O3`, retains OpenMP and C++11, and writes the separate binary `ebsynth/bin/ebsynth-cuda`. Existing CPU binary `ebsynth/bin/ebsynth` is preserved.

One attempt only, capped with `/usr/bin/timeout 300`:

```sh
timeout 300 sh build-linux-cuda-sm86.sh
```

**Result:** timeout exit 124 after measured 300.015 seconds. Compilation reached the CUDA device compiler `cicc` and remained there at the deadline. No complete CUDA executable was produced and no CUDA self-check or synthesis timing was performed. This is a bounded compilation-time blocker, not evidence of GPU runtime incompatibility.

Warnings recorded before timeout include vendored stb PNG transparency handling and `jzq.h` host/device declarations and host-only `std::min`/`std::max` calls in `clamp<int>`. No source/toolchain repairs or system package installation were attempted.

Evidence: `cuda-environment.log`, `build-cuda.log`, `cuda-setup-receipt.json`. CPU synthesis remains available and was previously validated with its tiny image self-check.

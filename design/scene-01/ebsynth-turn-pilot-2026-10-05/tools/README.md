# EbSynth local setup

Official source: https://github.com/jamriska/ebsynth

Source commit: `2f5c97c0c21a86bb7334dee61453623e6a3d41c3`.

The upstream README dedicates the code to the public domain and records an Adobe PatchMatch patent notice. This is the open-source image synthesizer CLI, not the newer proprietary EbSynth application.

The clone is local at `ebsynth/`; source and build scripts were inspected before compilation. No system package installation or project runtime changes were made.

Build command, run from the clone root:

```sh
sh build-linux-cpu_only.sh
```

This upstream script compiles `src/ebsynth.cpp`, `src/ebsynth_cpu.cpp`, and `src/ebsynth_nocuda.cpp`, with `g++`, `-DNDEBUG -O6 -fopenmp -Iinclude -std=c++11`. The image codecs are vendored stb headers. The compiler is `/usr/bin/g++`, GCC 16.2.1 (20260810). Runtime linkage is recorded in `dependencies.log` after build.

The upstream CUDA script uses obsolete `compute_30`; this machine has CUDA 13.4. The CPU route was selected without modifying upstream source or replacing the CUDA flags.

Compiler output is in `build-cpu.log`. GCC warned about a possible one-byte overflow in the vendored stb PNG transparency decoder at `src/stb_image.h:4505`. The bounded test inputs are opaque 8-bit RGB PNGs.

`selfcheck.py` creates three constant 32×32 RGB PNG fixtures using only Python standard-library code. The actual synthesis command and result are recorded in `selfcheck.log`; usage output is recorded in `usage.log`. EbSynth shows usage with no arguments and exits 1 by design; it does not support `--help`.

The build succeeded with exit 0. Executable: `ebsynth/bin/ebsynth`.

```sh
OMP_NUM_THREADS=2 timeout 30 ./ebsynth/bin/ebsynth \
  -style selfcheck/style.png \
  -guide selfcheck/source.png selfcheck/target.png \
  -output selfcheck/output.png -backend cpu \
  -patchsize 3 -pyramidlevels 1 -searchvoteiters 1 -patchmatchiters 1
```

The self-check exited 0 and wrote an image that Pillow 12.3.0 decoded as 32×32 RGB. Every output pixel is exactly `(192,96,32)`, matching the constant style fixture. This validates executable setup and basic synthesis/image I/O; it does not assess artistic quality or temporal stability.

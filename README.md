Fortran-Python Communication using Ctypes
-----------------------------------------

This repo demonstrates how it is possible to use Fortran code from Python if the Fortran code contains derived types.
This is not supported directly by f2py at the time of writing, which is why ctypes was used instead.

The repo contains a single fortran source file, `src/fortran/example.f90`, which contains a single `examle` module.
The shared library can be build with cmake, using the `CMakeLists.txt` file at the root of the repo. However, since the
source consists only of a single file, it can also easily be build manually. From the root of the repo:

```
gfortran -shared -fPIC src/fortran/example.f90 -o lib/example.so
```

The repo furthermore contains a single Python script: `src/python/example.py`. This script can be run after the shared
object has been built to test that it works as it should.

This example was inspired on the 
[Fortran Foreign Documentation](https://media.readthedocs.org/pdf/foreign-fortran/latest/foreign-fortran.pdf) 
document written by Danny Hermes.
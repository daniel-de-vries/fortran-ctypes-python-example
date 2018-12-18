import ctypes
import os
import time

import numpy as np

from multiprocessing import Pool

# Get the location of the shared library file.
here = os.path.dirname(__file__)
lib_file = os.path.abspath(os.path.join(here, '..', '..', 'lib', 'example.so'))


class UserDefined(ctypes.Structure):
    """Demonstrate how to wrap a Fortran derived type in Python using ctypes.

    Fields of the derived type are stored in the _fields_ attribute, which is a dict. Note that the data_ field is
    representing the Fortran data array. This is a 4x2 array in Fortran, but is stored internally in this object as a
    flat array of 8 c_doubles. Note also the syntax to achieve this: ctypes.c_double * 8.
    """
    _fields_ = [
        ('buzz', ctypes.c_double),
        ('broken', ctypes.c_double),
        ('how_many', ctypes.c_int),
        ('data_', ctypes.c_double * 8)
    ]

    @property
    def data(self):
        """Link to the data array stored in this Fortran derived type as a numpy array."""
        result = np.ctypeslib.as_array(self.data_)
        return result.reshape((4, 2), order='F')

    def __repr__(self):
        """Print a representation of the derived type."""
        template = (
            'UserDefined(buzz={self.buzz}, '
            'broken={self.broken}, '
            'how_many={self.how_many}, '
            'data={self.data})'
        )
        return template.format(self=self)


# This is how a dll/so library is loaded
lib_example = ctypes.cdll.LoadLibrary(lib_file)


def do_the_pointer_thing(some_int):
    """Store an integer in a Fortran derived type which is referred to only by a pointer.

    This function stores a given integer in a Fortran derived type. The only reference it holds to this derived type
    is a pointer to it. The function then sleeps a time of 1 / (1 + some_int) seconds. Finally, the function asks
    Fortran to print the integer it previously stored there using only the pointer to refer to it. If all goes well,
    the function should print the same integer twice.

    :param some_int: some integer to store in a Fortran derived type
    """
    # Convert some_int to a ctypes.c_int.
    c_some_int = ctypes.c_int(some_int)

    # This is the pointer which will allow Python to keep a handle on the Fortran derived type.
    m = ctypes.c_void_p()

    # Call the Fortran subroutine to actually construct the derived type in memory (handled by Fortran).
    lib_example.makeDerivedType(
        ctypes.byref(c_some_int),
        ctypes.byref(m)
    )

    # Sleep for a time inversely proportional to some_int.
    time.sleep(1./float(1 + some_int))

    # Retrieve the integer stored in the Fortran derived type using the pointer to it.
    c_same_int = ctypes.c_int()
    lib_example.examineDerivedType(
        m,
        ctypes.byref(c_same_int)
    )

    # Print the input integer and the one given back by Fortran. These should be the same.
    print('These two integers should be the same: {}, {}'.format(some_int, c_same_int.value))


def main():
    """Demonstrate how to use ctypes to use Fortran libraries."""
    # Create a UserDefined derived type in Fortran.
    buzz = ctypes.c_double(1.25)
    broken = ctypes.c_double(5.0)
    how_many = ctypes.c_int(1337)
    udf = UserDefined()
    lib_example.make_udf(
        ctypes.byref(buzz),
        ctypes.byref(broken),
        ctypes.byref(how_many),
        ctypes.byref(udf)
    )

    # Print the derived type.
    print('Hello from Python!')
    print(udf.__repr__())

    # Manipulate the derived type from Fortran.
    lib_example.use_udf(
        ctypes.byref(udf)
    )

    # Print it again to make sure we can see the manipulations Fortran made in Python too.
    print('Hello from Python!')
    print(udf.__repr__())

    # Call do_the_pointer_thing() 4 times, with the numbers 0, 1, 2, 3 respectively.
    # These calls are done consecutively, and due to the fact that the function sleeps a time inversely proportional to
    # the input integer, the calls should finish in inverse order. This gives each successive function call the change
    # to potentially interfere with the stored values of previous calls. But if all goes as expected, that is, if the
    # calls are independent of each other, then the integers should remain unchanged.
    pool = Pool(processes=4)
    pool.map(do_the_pointer_thing, range(4))

    # Pass a numpy array to a Fortran function
    doubleptr = ctypes.POINTER(ctypes.c_double)
    n = ctypes.c_int(10)
    arr = np.array(np.random.rand(n.value), dtype=ctypes.c_double)
    np.set_printoptions(3)
    print('{}'.format(arr))
    lib_example.printArray(ctypes.byref(n), arr.ctypes.data_as(doubleptr))


if __name__ == '__main__':
    main()

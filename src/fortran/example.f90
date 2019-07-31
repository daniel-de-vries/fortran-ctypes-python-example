module example
    use, intrinsic :: iso_c_binding, only: c_double, c_int, c_ptr, c_loc, c_f_pointer
    implicit none
    private
    public dp, make_udf, use_udf, makeDerivedType, examineDerivedType, printArray, UserDefined

    integer, parameter :: dp = kind(0.d0)

    type, bind(c) :: UserDefined
        real(c_double) :: buzz
        real(c_double) :: broken
        integer(c_int) :: how_many
        real(c_double) :: data(4, 2)
    end type UserDefined

    type :: SomeDerivedType
        integer :: someInteger
    end type SomeDerivedType

    type :: VariableLengthArrayType
        integer(c_int) :: size
        type(c_ptr) :: data
    end type VariableLengthArrayType

contains

    subroutine make_udf(buzz, broken, how_many, udf) bind(c, name='make_udf')
        real(c_double), intent(in) :: buzz, broken
        integer(c_int), intent(in) :: how_many
        type(UserDefined), intent(out) :: udf

        print *, 'Hello from Fortran!'
        print '("buzz: "(F5.2)", broken: "(F5.2)", now_many: "(I4))', buzz, broken, how_many

        udf = UserDefined(buzz, broken, how_many, reshape((/1, 2, 3, 4, 5, 6, 7, 8/), (/4, 2/)) )
    end subroutine make_udf

    subroutine use_udf(udf) bind(c, name='use_udf')
        type(UserDefined), intent(inout) :: udf

        udf%buzz = 10._dp
        udf%broken = 0._dp
        udf%how_many = 3
        udf%data = 4._dp

        print *, 'Hello from Fortran!'
        print '("buzz: "(F5.2)", broken: "(F5.2)", now_many: "(I4))', udf%buzz, udf%broken, udf%how_many
    end subroutine use_udf

    subroutine makeDerivedType(someInt, cdt) bind(c, name='makeDerivedType')
        integer, intent(in) :: someInt
        type(c_ptr) :: cdt
        type(SomeDerivedType), pointer :: fdt
        allocate(fdt)
        fdt%someInteger = someInt
        cdt = c_loc(fdt)
    end subroutine makeDerivedType

    subroutine examineDerivedType(this, someInt) bind(c, name='examineDerivedType')
        type(c_ptr), value :: this
        integer(c_int), intent(out) :: someInt
        type(SomeDerivedType), pointer :: that
        call c_f_pointer(this, that)
        someInt = that%someInteger
    end subroutine examineDerivedType

    subroutine printArray(n, array) bind(c, name='printArray')
        integer(c_int), intent(in) :: n
        real(c_double), intent(in) :: array(n)
        integer :: i
        print '("["100(F5.3,1X)"]")', (array(i), i=1, n)
    end subroutine printArray

    subroutine print2DArray(m, n, array) bind(c, name='print2DArray')
        integer(c_int), intent(in) :: m, n
        real(c_double), intent(in) :: array(m, n)
        integer :: i, j
        do i = 1, m
            if (i == 1) then
                print '("[["100(F5.3,1X)"]")', (array(i, j), j=1, n)
            elseif (i < m) then
                print '(" ["100(F5.3,1X)"]")', (array(i, j), j=1, n)
            else
                print '(" ["100(F5.3,1X)"]]")', (array(i, j), j=1, n)
            end if
        end do
    end subroutine print2DArray

    subroutine putArrayInUDT(n, array) bind(c, name='putArrayInUDT')
        integer(c_int), intent(in) :: n
        real(c_double), pointer, intent(in) :: array(:)
        type(VariableLengthArrayType) :: container

        container%size = n
        container%data = c_loc(array)

        call printArrayInUDT(container)
    end subroutine putArrayInUDT

    subroutine printArrayInUDT(container)
        type(VariableLengthArrayType) :: container
        real(c_double), pointer :: array(:)

        call c_f_pointer(container%data, array, [container%size])

        call printArray(container%size, array)
    end subroutine printArrayInUDT

end module example
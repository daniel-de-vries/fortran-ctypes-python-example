cmake_minimum_required(VERSION 3.13)
project(example Fortran)

set(
        ARCHIVE_OUTPUT_DIRECTORY "bin"
        LIBRARY_OUTPUT_DIRECTORY "bin"
        RUNTIME_OUTPUT_DIRECTORY "bin"
)

enable_language(Fortran)
add_library(example SHARED src/fortran/example.f90)
add_custom_command(TARGET example POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:example> ../lib/example.so
)

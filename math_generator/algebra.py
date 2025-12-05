from cffi import FFI

ffi = FFI()

with open("algebra.h", "r") as header:
    ffi.cdef(header.read())

library = ffi.dlopen("algebra.dll")

difficulty = 1 
problem = library.equation_linear(difficulty)
print("Сгенерированная задача:", ffi.string(problem).decode())
library.free_string(problem)  
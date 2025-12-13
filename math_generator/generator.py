import cffi

def DLL(dll_path: str, header_path: str):
    ffi = cffi.FFI()
    
    with open(header_path, "r", encoding="utf-8") as f:
        ffi.cdef(f.read())
    
    dll = ffi.dlopen(dll_path)
    return dll, ffi

generator, ffi = DLL("algebra.dll", "algebra.h")

def string(c_string, free_func=None) -> str:
    if c_string == ffi.NULL:
        return ""
    
    py_string = ffi.string(c_string).decode('utf-8')
    
    if free_func:
        free_func(c_string)
    elif hasattr(generator, 'free_string'):
        generator.free_string(c_string)
    
    return py_string

print(string(generator.equation_linear(1)))
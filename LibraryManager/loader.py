import os
import platform
import re
from pathlib import Path
from cffi import FFI

class Library:
    def __init__(self, name: str, header_path: str = "", search_path: str = "."):
        if not header_path:
            header_path = name + ".h"
        self.ffi = FFI()
        self._os = platform.system()
        self._dll_dir_handle = None
        self._load_library(name, header_path, search_path)

    def _define_lib_extension(self):
        if self._os == "Windows":
            ext = ".dll"
        elif self._os == "Darwin": 
            ext = ".dylib"
        elif self._os == "Linux":
            ext = ".so"
        return ext

    def _load_library(self, name: str, header_path: str, search_path: str):
        ext = self._define_lib_extension()
        
        dll_path = Path(search_path) / f"{name}{ext}"
        
        with open(header_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r'#.*', '', content)
        content = content.replace('extern "C"', '').replace('{', '').replace('}', '')
        
        if self._os == "Windows":
            self._target_type = "wchar_t*"
            content = content.replace('char16_t', 'wchar_t')
        else:
            self._target_type = "uint16_t*"
            content = "typedef unsigned short uint16_t;\n" + content.replace('char16_t', 'uint16_t')

        content = content.replace('VALIDATOR_API', '').replace('noexcept', '').replace('__stdcall', '')

        try:
            self.ffi.cdef(content)
            
            # На Windows 10+ добавляем директорию для поиска зависимостей DLL
            if self._os == "Windows" and hasattr(os, 'add_dll_directory'):
                try:
                    self._dll_dir_handle = os.add_dll_directory(str(Path(search_path).absolute()))
                except Exception as e:
                    print(f"Warning: Could not add DLL directory: {e}")
            
            self.lib = self.ffi.dlopen(str(dll_path.absolute()))
        except Exception as e:
            raise RuntimeError(f"CFFI cdef error: {e}")

    def utf16(self, text: str):
        """Возвращает объект, совместимый с целевым типом указателя"""
        if text is None:
            return self.ffi.NULL

        if self._os == "Windows":
            return text 
        else:
            encoded = text.encode('utf-16-le') + b'\x00\x00'
            return self.ffi.cast(self._target_type, self.ffi.from_buffer(encoded))


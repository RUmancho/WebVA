import platform
import re
from pathlib import Path
from cffi import FFI

class Library:
    def __init__(self, name: str, header_path: str, search_path: str = "."):
        self.ffi = FFI()
        self._os = platform.system()
        self._load_library(name, header_path, search_path)

    def _load_library(self, name: str, header_path: str, search_path: str):
        # Определение расширения
        ext = ".dll" if self._os == "Windows" else ".so"
        if self._os == "Darwin": ext = ".dylib"
        
        dll_path = Path(search_path) / f"{name}{ext}"
        
        with open(header_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Очистка заголовка
        content = re.sub(r'#.*', '', content)
        content = content.replace('extern "C"', '').replace('{', '').replace('}', '')
        
        # Настройка типов в зависимости от ОС
        if self._os == "Windows":
            # На Windows wchar_t = 2 байта. CFFI сам конвертирует str -> wchar_t*
            self._target_type = "wchar_t*"
            content = content.replace('char16_t', 'wchar_t')
        else:
            # На Linux wchar_t = 4 байта, поэтому используем uint16_t (2 байта)
            self._target_type = "uint16_t*"
            content = "typedef unsigned short uint16_t;\n" + content.replace('char16_t', 'uint16_t')

        content = content.replace('VALIDATOR_API', '').replace('noexcept', '').replace('__stdcall', '')

        try:
            self.ffi.cdef(content)
            self.lib = self.ffi.dlopen(str(dll_path.absolute()))
        except Exception as e:
            raise RuntimeError(f"CFFI cdef error: {e}")

    def utf16(self, text: str):
        """Возвращает объект, совместимый с целевым типом указателя"""
        if text is None:
            return self.ffi.NULL

        if self._os == "Windows":
            # Самый эффективный путь на Win: CFFI сделает всё за нас
            return text 
        else:
            encoded = text.encode('utf-16-le') + b'\x00\x00'
            return self.ffi.cast(self._target_type, self.ffi.from_buffer(encoded))


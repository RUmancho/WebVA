import ctypes

integer = ctypes.c_int

class Task(ctypes.Structure):
    _fields_ = [
        ("description", ctypes.c_wchar_p),
        ("solution", ctypes.c_wchar_p),
        ("answer", ctypes.c_wchar_p),
    ]

class Level(integer):
    EASY = 1
    MEDIUM = 2
    HARD = 3

lib = ctypes.CDLL("./algebra.dll")

lib.linear_equation.argtypes = [Level] 
lib.linear_equation.restype = Task  

lib.linear_inequality.argtypes = [Level] 
lib.linear_inequality.restype = Task  

lib.reset.argtypes = []
lib.reset.restype = None

def linear_equation(difficulty: Level) -> Task:
    return lib.linear_equation(difficulty)

def linear_inequality(difficulty: Level) -> Task:
    return lib.linear_inequality(difficulty)


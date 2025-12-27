import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from LibraryManager import loader

GENERATOR_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATOR_DLL = loader.Library("algebra", os.path.join(GENERATOR_DIR, "algebra.h"), GENERATOR_DIR)

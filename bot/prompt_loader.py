from pathlib import Path
import os, sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from logger import console

PROMPTS_DIR = Path(__file__).parent / "prompts"

python_filename = "prompt_loader"

@console.debug(python_filename)
def filereader(filename: str) -> str:
    """Загружает промпт из файла в папке prompts."""
    try:
        filepath = PROMPTS_DIR / filename
        with open(filepath, 'r', encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка загрузки промпта {filename}: {e}")
        return ""

@console.debug(python_filename)
def load_prompt_with_format(filename: str, **kwargs) -> str:
    """Загружает промпт из файла и форматирует его с переданными параметрами."""
    prompt_template = filereader(filename)
    if not prompt_template:
        return ""
    
    # Если есть параметры и в шаблоне есть плейсхолдеры, форматируем
    if kwargs and "{" in prompt_template and "}" in prompt_template:
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            print(f"Предупреждение: отсутствует параметр для промпта {filename}: {e}")
            return prompt_template
    
    return prompt_template


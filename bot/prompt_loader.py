from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(filename: str) -> str:
    """Загружает промпт из файла в папке prompts."""
    try:
        filepath = PROMPTS_DIR / filename
        with open(filepath, 'r', encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка загрузки промпта {filename}: {e}")
        return ""

def load_prompt_with_format(filename: str, **kwargs) -> str:
    """Загружает промпт из файла и форматирует его с переданными параметрами."""
    prompt_template = load_prompt(filename)
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


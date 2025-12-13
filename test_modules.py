"""Тест модулей"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 50)
print("Тестирование модулей")
print("=" * 50)

# Тест math_generator
try:
    from math_generator import get_math_generator
    gen = get_math_generator()
    print(f"\n✓ math_generator загружен")
    print(f"  - Доступен: {gen.is_available}")
    print(f"  - DLL: {gen.dll_available}")
    
    # Генерируем задачу
    problem = gen.generate_problem_by_topic("Линейные уравнения", "Средний")
    if problem:
        print(f"  - Пример: {problem['question']}")
        print(f"  - Ответ: {problem['correct_answer']}")
    else:
        print("  - Задача не сгенерирована")
except Exception as e:
    print(f"\n✗ math_generator: {e}")

# Тест physics
try:
    from formulas.physics_python import Force, Energy
    f = Force.gravity(10)
    print(f"\n✓ physics_python загружен")
    print(f"  - Сила тяжести 10кг: {f} Н")
except Exception as e:
    print(f"\n✗ physics_python: {e}")

print("\n" + "=" * 50)
print("Тестирование завершено")
print("=" * 50)

"""
Python wrapper для вызова функций из physics.dll
Использует ctypes для взаимодействия с C++ DLL
"""
import os
import sys
from pathlib import Path
from ctypes import CDLL, c_double, c_int, POINTER
from typing import Optional

# Получаем путь к DLL
CURRENT_DIR = Path(__file__).parent
DLL_PATH = CURRENT_DIR / "physics.dll"

# Глобальная переменная для хранения загруженной DLL
_PHYSICS_DLL = None
_DLL_LOADED = False
_DLL_LOAD_ERROR = None


def _load_dll():
    """Загружает DLL один раз при импорте модуля"""
    global _PHYSICS_DLL, _DLL_LOADED, _DLL_LOAD_ERROR
    
    # Если уже загружена, возвращаем
    if _DLL_LOADED and _PHYSICS_DLL is not None:
        return _PHYSICS_DLL
    
    # Если была ошибка загрузки, выбрасываем её
    if _DLL_LOAD_ERROR is not None:
        raise _DLL_LOAD_ERROR
    
    try:
        if not DLL_PATH.exists():
            raise FileNotFoundError(f"DLL файл не найден: {DLL_PATH}")
        
        _PHYSICS_DLL = CDLL(str(DLL_PATH))
        
        # Настройка типов возвращаемых значений для всех функций
        # Все функции возвращают double
        _PHYSICS_DLL.gravity.argtypes = [c_double, c_double]
        _PHYSICS_DLL.gravity.restype = c_double
        
        _PHYSICS_DLL.Newton_second_law.argtypes = [c_double, c_double]
        _PHYSICS_DLL.Newton_second_law.restype = c_double
        
        _PHYSICS_DLL.universal_gravitation.argtypes = [c_double, c_double, c_double, c_double]
        _PHYSICS_DLL.universal_gravitation.restype = c_double
        
        _PHYSICS_DLL.friction.argtypes = [c_double, c_double]
        _PHYSICS_DLL.friction.restype = c_double
        
        _PHYSICS_DLL.archimedes.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.archimedes.restype = c_double
        
        _PHYSICS_DLL.coulomb.argtypes = [c_double, c_double, c_double, c_double]
        _PHYSICS_DLL.coulomb.restype = c_double
        
        _PHYSICS_DLL.lorentz.argtypes = [c_double, c_double, c_double, c_double]
        _PHYSICS_DLL.lorentz.restype = c_double
        
        _PHYSICS_DLL.ampere.argtypes = [c_double, c_double, c_double, c_double]
        _PHYSICS_DLL.ampere.restype = c_double
        
        _PHYSICS_DLL.centripetal.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.centripetal.restype = c_double
        
        _PHYSICS_DLL.pressure.argtypes = [c_double, c_double]
        _PHYSICS_DLL.pressure.restype = c_double
        
        _PHYSICS_DLL.hydrostatic.argtypes = [c_double, c_double, c_double, c_double]
        _PHYSICS_DLL.hydrostatic.restype = c_double
        
        _PHYSICS_DLL.kinetic.argtypes = [c_double, c_double]
        _PHYSICS_DLL.kinetic.restype = c_double
        
        _PHYSICS_DLL.potential.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.potential.restype = c_double
        
        _PHYSICS_DLL.elastic_potential.argtypes = [c_double, c_double]
        _PHYSICS_DLL.elastic_potential.restype = c_double
        
        _PHYSICS_DLL.rotational_kinetic.argtypes = [c_double, c_double]
        _PHYSICS_DLL.rotational_kinetic.restype = c_double
        
        _PHYSICS_DLL.capacitor.argtypes = [c_double, c_double]
        _PHYSICS_DLL.capacitor.restype = c_double
        
        _PHYSICS_DLL.thermal.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.thermal.restype = c_double
        
        _PHYSICS_DLL.combustion.argtypes = [c_double, c_double]
        _PHYSICS_DLL.combustion.restype = c_double
        
        _PHYSICS_DLL.work_constant_force.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.work_constant_force.restype = c_double
        
        _PHYSICS_DLL.work_variable_force_linear.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.work_variable_force_linear.restype = c_double
        
        _PHYSICS_DLL.work_gas_isobaric.argtypes = [c_double, c_double]
        _PHYSICS_DLL.work_gas_isobaric.restype = c_double
        
        _PHYSICS_DLL.work_electric_field.argtypes = [c_double, c_double]
        _PHYSICS_DLL.work_electric_field.restype = c_double
        
        _PHYSICS_DLL.work_against_friction.argtypes = [c_double, c_double]
        _PHYSICS_DLL.work_against_friction.restype = c_double
        
        _PHYSICS_DLL.useful_work.argtypes = [c_double, c_double]
        _PHYSICS_DLL.useful_work.restype = c_double
        
        _PHYSICS_DLL.work_kinetic_energy_change.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.work_kinetic_energy_change.restype = c_double
        
        _PHYSICS_DLL.work_potential_energy_change.argtypes = [c_double, c_double, c_double, c_double]
        _PHYSICS_DLL.work_potential_energy_change.restype = c_double
        
        _PHYSICS_DLL.work_elastic_force.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.work_elastic_force.restype = c_double
        
        _PHYSICS_DLL.rest_energy.argtypes = [c_double]
        _PHYSICS_DLL.rest_energy.restype = c_double
        
        _PHYSICS_DLL.photon_energy.argtypes = [c_double]
        _PHYSICS_DLL.photon_energy.restype = c_double
        
        _PHYSICS_DLL.magnetic_energy.argtypes = [c_double, c_double]
        _PHYSICS_DLL.magnetic_energy.restype = c_double
        
        _PHYSICS_DLL.chemical_energy.argtypes = [c_double, c_double]
        _PHYSICS_DLL.chemical_energy.restype = c_double
        
        _PHYSICS_DLL.activation_energy.argtypes = [c_double, c_double, c_double]
        _PHYSICS_DLL.activation_energy.restype = c_double
        
        _PHYSICS_DLL.calculate_efficiency.argtypes = [c_double, c_double]
        _PHYSICS_DLL.calculate_efficiency.restype = c_double
        
        _PHYSICS_DLL.calculate_power.argtypes = [c_double, c_double]
        _PHYSICS_DLL.calculate_power.restype = c_double
        
        _PHYSICS_DLL.calculate_work_from_power.argtypes = [c_double, c_double]
        _PHYSICS_DLL.calculate_work_from_power.restype = c_double
        
        _DLL_LOADED = True
        print(f"DLL успешно загружена: {DLL_PATH}")
        return _PHYSICS_DLL
        
    except Exception as e:
        _DLL_LOAD_ERROR = e
        print(f"Ошибка загрузки DLL: {e}")
        raise


# Загружаем DLL один раз при импорте модуля
try:
    _load_dll()
except Exception:
    # Ошибка загрузки будет обработана при первом использовании
    pass


# Класс для работы с силами
class Force:
    """Функции для расчета сил"""
    
    @staticmethod
    def gravity(m: float, g: Optional[float] = None) -> float:
        """Сила тяжести: F = m * g"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            if g is None:
                from constants.physics import g as default_g
                g = default_g
            return _PHYSICS_DLL.gravity(c_double(m), c_double(g))
        except Exception as e:
            print(f"Ошибка расчета силы тяжести: {e}")
            raise
    
    @staticmethod
    def newton_second_law(m: float, a: float) -> float:
        """Второй закон Ньютона: F = m * a"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.Newton_second_law(c_double(m), c_double(a))
        except Exception as e:
            print(f"Ошибка расчета по второму закону Ньютона: {e}")
            raise
    
    @staticmethod
    def universal_gravitation(m1: float, m2: float, r: float, G: Optional[float] = None) -> float:
        """Закон всемирного тяготения: F = G * m1 * m2 / r²"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            if G is None:
                from constants.physics import G as default_G
                G = default_G
            return _PHYSICS_DLL.universal_gravitation(c_double(m1), c_double(m2), c_double(r), c_double(G))
        except Exception as e:
            print(f"Ошибка расчета всемирного тяготения: {e}")
            raise
    
    @staticmethod
    def friction(u: float, N: float) -> float:
        """Сила трения: F = μ * N"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.friction(c_double(u), c_double(N))
        except Exception as e:
            print(f"Ошибка расчета силы трения: {e}")
            raise
    
    @staticmethod
    def archimedes(p: float, V: float, g: Optional[float] = None) -> float:
        """Сила Архимеда: F = ρ * V * g"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            if g is None:
                from constants.physics import g as default_g
                g = default_g
            return _PHYSICS_DLL.archimedes(c_double(p), c_double(V), c_double(g))
        except Exception as e:
            print(f"Ошибка расчета силы Архимеда: {e}")
            raise
    
    @staticmethod
    def coulomb(q1: float, q2: float, r: float, k: Optional[float] = None) -> float:
        """Закон Кулона: F = k * q1 * q2 / r²"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            if k is None:
                from constants.physics import k as default_k
                k = default_k
            return _PHYSICS_DLL.coulomb(c_double(q1), c_double(q2), c_double(r), c_double(k))
        except Exception as e:
            print(f"Ошибка расчета силы Кулона: {e}")
            raise
    
    @staticmethod
    def lorentz(q: float, V: float, B: float, angle: float) -> float:
        """Сила Лоренца: F = q * V * B * sin(angle)"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.lorentz(c_double(q), c_double(V), c_double(B), c_double(angle))
        except Exception as e:
            print(f"Ошибка расчета силы Лоренца: {e}")
            raise
    
    @staticmethod
    def ampere(B: float, I: float, L: float, angle: float) -> float:
        """Сила Ампера: F = B * I * L * sin(angle)"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.ampere(c_double(B), c_double(I), c_double(L), c_double(angle))
        except Exception as e:
            print(f"Ошибка расчета силы Ампера: {e}")
            raise
    
    @staticmethod
    def centripetal(m: float, V: float, r: float) -> float:
        """Центростремительная сила: F = m * V² / r"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.centripetal(c_double(m), c_double(V), c_double(r))
        except Exception as e:
            print(f"Ошибка расчета центростремительной силы: {e}")
            raise
    
    @staticmethod
    def pressure(P: float, S: float) -> float:
        """Сила давления: F = P * S"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.pressure(c_double(P), c_double(S))
        except Exception as e:
            print(f"Ошибка расчета силы давления: {e}")
            raise
    
    @staticmethod
    def hydrostatic(p: float, h: float, S: float, g: Optional[float] = None) -> float:
        """Гидростатическое давление: F = ρ * g * h * S"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            if g is None:
                from constants.physics import g as default_g
                g = default_g
            return _PHYSICS_DLL.hydrostatic(c_double(p), c_double(h), c_double(S), c_double(g))
        except Exception as e:
            print(f"Ошибка расчета гидростатического давления: {e}")
            raise


# Класс для работы с энергией
class Energy:
    """Функции для расчета энергии"""
    
    @staticmethod
    def kinetic(m: float, V: float) -> float:
        """Кинетическая энергия: E = m * V² / 2"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.kinetic(c_double(m), c_double(V))
        except Exception as e:
            print(f"Ошибка расчета кинетической энергии: {e}")
            raise
    
    @staticmethod
    def potential(m: float, h: float, g: Optional[float] = None) -> float:
        """Потенциальная энергия: E = m * g * h"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            if g is None:
                from constants.physics import g as default_g
                g = default_g
            return _PHYSICS_DLL.potential(c_double(m), c_double(h), c_double(g))
        except Exception as e:
            print(f"Ошибка расчета потенциальной энергии: {e}")
            raise
    
    @staticmethod
    def elastic_potential(k: float, x: float) -> float:
        """Потенциальная энергия упругой деформации: E = k * x² / 2"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.elastic_potential(c_double(k), c_double(x))
        except Exception as e:
            print(f"Ошибка расчета потенциальной энергии упругости: {e}")
            raise
    
    @staticmethod
    def rotational_kinetic(I: float, w: float) -> float:
        """Кинетическая энергия вращения: E = I * ω² / 2"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.rotational_kinetic(c_double(I), c_double(w))
        except Exception as e:
            print(f"Ошибка расчета кинетической энергии вращения: {e}")
            raise
    
    @staticmethod
    def capacitor(C: float, U: float) -> float:
        """Энергия конденсатора: E = C * U² / 2"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.capacitor(c_double(C), c_double(U))
        except Exception as e:
            print(f"Ошибка расчета энергии конденсатора: {e}")
            raise
    
    @staticmethod
    def thermal(m: float, c: float, dt: float) -> float:
        """Тепловая энергия: Q = m * c * ΔT"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.thermal(c_double(m), c_double(c), c_double(dt))
        except Exception as e:
            print(f"Ошибка расчета тепловой энергии: {e}")
            raise
    
    @staticmethod
    def combustion(m: float, q: float) -> float:
        """Энергия сгорания: Q = m * q"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.combustion(c_double(m), c_double(q))
        except Exception as e:
            print(f"Ошибка расчета энергии сгорания: {e}")
            raise
    
    @staticmethod
    def work_constant_force(F: float, s: float, angle_degrees: float = 0) -> float:
        """Работа постоянной силы: A = F * s * cos(angle)"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.work_constant_force(c_double(F), c_double(s), c_double(angle_degrees))
        except Exception as e:
            print(f"Ошибка расчета работы постоянной силы: {e}")
            raise
    
    @staticmethod
    def work_variable_force_linear(F_initial: float, F_final: float, s: float) -> float:
        """Работа переменной силы (линейная зависимость): A = (F_initial + F_final) * s / 2"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.work_variable_force_linear(c_double(F_initial), c_double(F_final), c_double(s))
        except Exception as e:
            print(f"Ошибка расчета работы переменной силы: {e}")
            raise
    
    @staticmethod
    def work_gas_isobaric(P: float, dV: float) -> float:
        """Работа газа при изобарном процессе: A = P * ΔV"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.work_gas_isobaric(c_double(P), c_double(dV))
        except Exception as e:
            print(f"Ошибка расчета работы газа: {e}")
            raise
    
    @staticmethod
    def work_electric_field(q: float, U: float) -> float:
        """Работа электрического поля: A = q * U"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.work_electric_field(c_double(q), c_double(U))
        except Exception as e:
            print(f"Ошибка расчета работы электрического поля: {e}")
            raise
    
    @staticmethod
    def work_against_friction(F_friction: float, s: float) -> float:
        """Работа против силы трения: A = F_friction * s"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.work_against_friction(c_double(F_friction), c_double(s))
        except Exception as e:
            print(f"Ошибка расчета работы против трения: {e}")
            raise
    
    @staticmethod
    def useful_work(total_work: float, efficiency: float) -> float:
        """Полезная работа: A_useful = A_total * η"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.useful_work(c_double(total_work), c_double(efficiency))
        except Exception as e:
            print(f"Ошибка расчета полезной работы: {e}")
            raise
    
    @staticmethod
    def work_kinetic_energy_change(m: float, V_initial: float, V_final: float) -> float:
        """Работа через изменение кинетической энергии: A = m * (V_final² - V_initial²) / 2"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.work_kinetic_energy_change(c_double(m), c_double(V_initial), c_double(V_final))
        except Exception as e:
            print(f"Ошибка расчета работы через изменение кинетической энергии: {e}")
            raise
    
    @staticmethod
    def work_potential_energy_change(m: float, h_initial: float, h_final: float, g: Optional[float] = None) -> float:
        """Работа через изменение потенциальной энергии: A = m * g * (h_final - h_initial)"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            if g is None:
                from constants.physics import g as default_g
                g = default_g
            return _PHYSICS_DLL.work_potential_energy_change(c_double(m), c_double(h_initial), c_double(h_final), c_double(g))
        except Exception as e:
            print(f"Ошибка расчета работы через изменение потенциальной энергии: {e}")
            raise
    
    @staticmethod
    def work_elastic_force(k: float, x_initial: float, x_final: float) -> float:
        """Работа упругой силы: A = k * (x_final² - x_initial²) / 2"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.work_elastic_force(c_double(k), c_double(x_initial), c_double(x_final))
        except Exception as e:
            print(f"Ошибка расчета работы упругой силы: {e}")
            raise
    
    @staticmethod
    def rest_energy(m: float) -> float:
        """Энергия покоя: E = m * c²"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.rest_energy(c_double(m))
        except Exception as e:
            print(f"Ошибка расчета энергии покоя: {e}")
            raise
    
    @staticmethod
    def photon_energy(frequency: float) -> float:
        """Энергия фотона: E = h * f"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.photon_energy(c_double(frequency))
        except Exception as e:
            print(f"Ошибка расчета энергии фотона: {e}")
            raise
    
    @staticmethod
    def magnetic_energy(L: float, I: float) -> float:
        """Энергия магнитного поля: E = L * I² / 2"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.magnetic_energy(c_double(L), c_double(I))
        except Exception as e:
            print(f"Ошибка расчета энергии магнитного поля: {e}")
            raise
    
    @staticmethod
    def chemical_energy(moles: float, bond_energy_per_mole: float) -> float:
        """Химическая энергия: E = n * E_bond"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.chemical_energy(c_double(moles), c_double(bond_energy_per_mole))
        except Exception as e:
            print(f"Ошибка расчета химической энергии: {e}")
            raise
    
    @staticmethod
    def activation_energy(pre_exponential: float, rate_constant: float, T: float) -> float:
        """Энергия активации: E_a = -R * T * ln(k / A)"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.activation_energy(c_double(pre_exponential), c_double(rate_constant), c_double(T))
        except Exception as e:
            print(f"Ошибка расчета энергии активации: {e}")
            raise


# Класс для утилит
class PhysicsUtils:
    """Утилиты для физических расчетов"""
    
    @staticmethod
    def calculate_efficiency(useful_work: float, total_work: float) -> float:
        """КПД: η = A_useful / A_total"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.calculate_efficiency(c_double(useful_work), c_double(total_work))
        except Exception as e:
            print(f"Ошибка расчета КПД: {e}")
            raise
    
    @staticmethod
    def calculate_power(work: float, time: float) -> float:
        """Мощность: P = A / t"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.calculate_power(c_double(work), c_double(time))
        except Exception as e:
            print(f"Ошибка расчета мощности: {e}")
            raise
    
    @staticmethod
    def calculate_work_from_power(power: float, time: float) -> float:
        """Работа из мощности: A = P * t"""
        try:
            if _PHYSICS_DLL is None:
                _load_dll()
            return _PHYSICS_DLL.calculate_work_from_power(c_double(power), c_double(time))
        except Exception as e:
            print(f"Ошибка расчета работы из мощности: {e}")
            raise

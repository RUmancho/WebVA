"""
Python реализация физических формул
Полная копия функциональности из physics.cpp
"""
import math
from typing import Optional

# Константы
class Constants:
    G = 6.67430e-11  # Гравитационная постоянная, Н·м²/кг²
    k = 8.987551789e9  # Постоянная Кулона, Н·м²/Кл²
    pi = 3.14159265358979323846
    g = 9.80665  # Ускорение свободного падения, м/с²
    c = 299792458.0  # Скорость света, м/с
    h = 6.62607015e-34  # Постоянная Планка, Дж·с
    R = 8.314462618  # Универсальная газовая постоянная, Дж/(моль·К)


def radians(angle: float) -> float:
    """Преобразует угол из градусов в радианы"""
    return angle * Constants.pi / 180.0


# ========== СИЛЫ (Force) ==========
class Force:
    """Функции для расчета сил"""
    
    @staticmethod
    def gravity(m: float, g: Optional[float] = None) -> float:
        """Сила тяжести: F = m * g"""
        if g is None:
            g = Constants.g
        return m * g
    
    @staticmethod
    def newton_second_law(m: float, a: float) -> float:
        """Второй закон Ньютона: F = m * a"""
        return m * a
    
    @staticmethod
    def universal_gravitation(m1: float, m2: float, r: float, G: Optional[float] = None) -> float:
        """Закон всемирного тяготения: F = G * m1 * m2 / r²"""
        if G is None:
            G = Constants.G
        if r == 0:
            return 0
        return G * (m1 * m2) / (r * r)
    
    @staticmethod
    def friction(u: float, N: float) -> float:
        """Сила трения: F = μ * N"""
        return u * N
    
    @staticmethod
    def archimedes(p: float, V: float, g: Optional[float] = None) -> float:
        """Сила Архимеда: F = ρ * V * g"""
        if g is None:
            g = Constants.g
        return p * g * V
    
    @staticmethod
    def coulomb(q1: float, q2: float, r: float, k: Optional[float] = None) -> float:
        """Закон Кулона: F = k * q1 * q2 / r²"""
        if k is None:
            k = Constants.k
        if r == 0:
            return 0
        return k * (q1 * q2) / (r * r)
    
    @staticmethod
    def lorentz(q: float, V: float, B: float, angle: float) -> float:
        """Сила Лоренца: F = q * V * B * sin(angle)"""
        return q * V * B * math.sin(radians(angle))
    
    @staticmethod
    def ampere(B: float, I: float, L: float, angle: float) -> float:
        """Сила Ампера: F = B * I * L * sin(angle)"""
        return B * I * L * math.sin(radians(angle))
    
    @staticmethod
    def centripetal(m: float, V: float, r: float) -> float:
        """Центростремительная сила: F = m * V² / r"""
        if r == 0:
            return 0
        return m * V * V / r
    
    @staticmethod
    def pressure(P: float, S: float) -> float:
        """Сила давления: F = P * S"""
        return P * S
    
    @staticmethod
    def hydrostatic(p: float, h: float, S: float, g: Optional[float] = None) -> float:
        """Гидростатическое давление: F = ρ * g * h * S"""
        if g is None:
            g = Constants.g
        return p * g * h * S
    
    # Обратные формулы
    @staticmethod
    def gravity_mass(F: float, g: Optional[float] = None) -> float:
        """Масса из силы тяжести: m = F / g"""
        if g is None:
            g = Constants.g
        if g == 0:
            return 0
        return F / g
    
    @staticmethod
    def newton_mass(F: float, a: float) -> float:
        """Масса из второго закона Ньютона: m = F / a"""
        if a == 0:
            return 0
        return F / a
    
    @staticmethod
    def newton_acceleration(F: float, m: float) -> float:
        """Ускорение из второго закона Ньютона: a = F / m"""
        if m == 0:
            return 0
        return F / m
    
    @staticmethod
    def centripetal_mass(F: float, V: float, r: float) -> float:
        """Масса из центростремительной силы: m = F * r / V²"""
        if V == 0 or r == 0:
            return 0
        return (F * r) / (V * V)
    
    @staticmethod
    def centripetal_velocity(F: float, m: float, r: float) -> float:
        """Скорость из центростремительной силы: V = sqrt(F * r / m)"""
        if m == 0 or r == 0:
            return 0
        return math.sqrt((F * r) / m)
    
    @staticmethod
    def centripetal_radius(F: float, m: float, V: float) -> float:
        """Радиус из центростремительной силы: r = m * V² / F"""
        if m == 0 or V == 0:
            return 0
        return (m * V * V) / F


# ========== ЭНЕРГИЯ (Energy) ==========
class Energy:
    """Функции для расчета энергии"""
    
    @staticmethod
    def kinetic(m: float, V: float) -> float:
        """Кинетическая энергия: E = m * V² / 2"""
        return 0.5 * m * V * V
    
    @staticmethod
    def potential(m: float, h: float, g: Optional[float] = None) -> float:
        """Потенциальная энергия: E = m * g * h"""
        if g is None:
            g = Constants.g
        return m * g * h
    
    @staticmethod
    def elastic_potential(k: float, x: float) -> float:
        """Потенциальная энергия упругой деформации: E = k * x² / 2"""
        return 0.5 * k * x * x
    
    @staticmethod
    def rotational_kinetic(I: float, w: float) -> float:
        """Кинетическая энергия вращения: E = I * ω² / 2"""
        return 0.5 * I * w * w
    
    @staticmethod
    def capacitor(C: float, U: float) -> float:
        """Энергия конденсатора: E = C * U² / 2"""
        return 0.5 * C * U * U
    
    @staticmethod
    def thermal(m: float, c: float, dt: float) -> float:
        """Тепловая энергия: Q = m * c * ΔT"""
        return m * c * dt
    
    @staticmethod
    def combustion(m: float, q: float) -> float:
        """Энергия сгорания: Q = m * q"""
        return m * q
    
    @staticmethod
    def work_constant_force(F: float, s: float, angle_degrees: float = 0) -> float:
        """Работа постоянной силы: A = F * s * cos(α)"""
        return F * s * math.cos(radians(angle_degrees))
    
    @staticmethod
    def work_variable_force_linear(F_initial: float, F_final: float, s: float) -> float:
        """Работа переменной силы (линейная): A = (F₁ + F₂) * s / 2"""
        return 0.5 * (F_initial + F_final) * s
    
    @staticmethod
    def work_gas_isobaric(P: float, dV: float) -> float:
        """Работа газа (изобарный процесс): A = P * ΔV"""
        return P * dV
    
    @staticmethod
    def work_electric_field(q: float, U: float) -> float:
        """Работа электрического поля: A = q * U"""
        return q * U
    
    @staticmethod
    def work_against_friction(F_friction: float, s: float) -> float:
        """Работа против трения: A = F_friction * s"""
        return F_friction * s
    
    @staticmethod
    def useful_work(total_work: float, efficiency: float) -> float:
        """Полезная работа: A_useful = A_total * η"""
        return total_work * efficiency
    
    @staticmethod
    def work_kinetic_energy_change(m: float, V_initial: float, V_final: float) -> float:
        """Работа через изменение кинетической энергии: A = m * (V₂² - V₁²) / 2"""
        return 0.5 * m * (V_final * V_final - V_initial * V_initial)
    
    @staticmethod
    def work_potential_energy_change(m: float, h_initial: float, h_final: float, g: Optional[float] = None) -> float:
        """Работа через изменение потенциальной энергии: A = m * g * (h₂ - h₁)"""
        if g is None:
            g = Constants.g
        return m * g * (h_final - h_initial)
    
    @staticmethod
    def work_elastic_force(k: float, x_initial: float, x_final: float) -> float:
        """Работа упругой силы: A = k * (x₂² - x₁²) / 2"""
        return 0.5 * k * (x_final * x_final - x_initial * x_initial)
    
    @staticmethod
    def rest_energy(m: float) -> float:
        """Энергия покоя: E = m * c²"""
        return m * Constants.c * Constants.c
    
    @staticmethod
    def photon_energy(frequency: float) -> float:
        """Энергия фотона: E = h * f"""
        return Constants.h * frequency
    
    @staticmethod
    def magnetic_energy(L: float, I: float) -> float:
        """Магнитная энергия: E = L * I² / 2"""
        return 0.5 * L * I * I
    
    @staticmethod
    def chemical_energy(moles: float, bond_energy_per_mole: float) -> float:
        """Химическая энергия: E = n * E_bond"""
        return moles * bond_energy_per_mole
    
    @staticmethod
    def activation_energy(pre_exponential: float, rate_constant: float, T: float) -> float:
        """Энергия активации: E_a = -R * T * ln(k / A)"""
        if pre_exponential == 0 or rate_constant <= 0 or T <= 0:
            return 0
        return -Constants.R * T * math.log(rate_constant / pre_exponential)
    
    # Обратные формулы
    @staticmethod
    def kinetic_mass(E: float, V: float) -> float:
        """Масса из кинетической энергии: m = 2 * E / V²"""
        if V == 0:
            return 0
        return (2 * E) / (V * V)
    
    @staticmethod
    def kinetic_velocity(E: float, m: float) -> float:
        """Скорость из кинетической энергии: V = sqrt(2 * E / m)"""
        if m == 0:
            return 0
        return math.sqrt((2 * E) / m)
    
    @staticmethod
    def potential_mass(E: float, h: float, g: Optional[float] = None) -> float:
        """Масса из потенциальной энергии: m = E / (g * h)"""
        if g is None:
            g = Constants.g
        if h == 0 or g == 0:
            return 0
        return E / (g * h)
    
    @staticmethod
    def potential_height(E: float, m: float, g: Optional[float] = None) -> float:
        """Высота из потенциальной энергии: h = E / (m * g)"""
        if g is None:
            g = Constants.g
        if m == 0 or g == 0:
            return 0
        return E / (m * g)
    
    @staticmethod
    def elastic_potential_k(E: float, x: float) -> float:
        """Жесткость из потенциальной энергии упругости: k = 2 * E / x²"""
        if x == 0:
            return 0
        return (2 * E) / (x * x)
    
    @staticmethod
    def elastic_potential_x(E: float, k: float) -> float:
        """Деформация из потенциальной энергии упругости: x = sqrt(2 * E / k)"""
        if k == 0:
            return 0
        return math.sqrt((2 * E) / k)


# ========== УТИЛИТЫ (PhysicsUtils) ==========
class PhysicsUtils:
    """Утилиты для физических расчетов"""
    
    @staticmethod
    def calculate_efficiency(useful_work: float, total_work: float) -> float:
        """КПД: η = A_useful / A_total"""
        if total_work == 0:
            return 0
        return useful_work / total_work
    
    @staticmethod
    def calculate_power(work: float, time: float) -> float:
        """Мощность: P = A / t"""
        if time == 0:
            return 0
        return work / time
    
    @staticmethod
    def calculate_work_from_power(power: float, time: float) -> float:
        """Работа из мощности: A = P * t"""
        return power * time
    
    @staticmethod
    def momentum(m: float, v: float) -> float:
        """Импульс: p = m * v"""
        return m * v
    
    @staticmethod
    def impulse(F: float, t: float) -> float:
        """Импульс силы: J = F * t"""
        return F * t
    
    @staticmethod
    def pressure_from_force(F: float, S: float) -> float:
        """Давление из силы: P = F / S"""
        if S == 0:
            return 0
        return F / S
    
    @staticmethod
    def density(m: float, V: float) -> float:
        """Плотность: ρ = m / V"""
        if V == 0:
            return 0
        return m / V
    
    @staticmethod
    def volume_from_density(m: float, p: float) -> float:
        """Объем из плотности: V = m / ρ"""
        if p == 0:
            return 0
        return m / p
    
    @staticmethod
    def mass_from_density(p: float, V: float) -> float:
        """Масса из плотности: m = ρ * V"""
        return p * V


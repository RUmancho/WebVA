import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import constants.physics as const
except ImportError:
    print("Ошибка: не удалось импортировать constants.physics")
    raise

class Mechanics:
    class NewtonSecondLaw:
        F = lambda m, a: m * a
        m = lambda F, a: F / a
        a = lambda F, m: F / m

    class Gravity:
        F = lambda m1, m2, r, G=const.G: G * m1 * m2 / r**2
        m1 = lambda F, m2, r, G=const.G: F * r**2 / (G * m2)
        m2 = lambda F, m1, r, G=const.G: F * r**2 / (G * m1)
        r = lambda F, m1, m2, G=const.G: (G * m1 * m2 / F)**0.5

    class Energy:
        kinetic = lambda m, v: 0.5 * m * v**2
        potential = lambda m, h, g=const.g: m * g * h

    class Momentum:
        p = lambda m, v: m * v
        m = lambda p, v: p / v
        v = lambda p, m: p / m

class Thermodynamics:
    class IdealGas:
        PV = lambda n, R, T: n * R * T
        n = lambda P, V, R, T: P * V / (R * T)
        T = lambda P, V, n, R: P * V / (n * R)

    class Heat:
        Q = lambda m, c, ΔT: m * c * ΔT
        c = lambda Q, m, ΔT: Q / (m * ΔT)
        ΔT = lambda Q, m, c: Q / (m * c)

class Electromagnetism:
    class Coulomb:
        F = lambda q1, q2, r, k=const.k: k * q1 * q2 / r**2
        q1 = lambda F, q2, r, k=const.k: F * r**2 / (k * q2)
        r = lambda F, q1, q2, k=const.k: (k * q1 * q2 / F)**0.5

    class Ohm:
        V = lambda I, R: I * R
        I = lambda V, R: V / R
        R = lambda V, I: V / I

    class Power:
        P = lambda V, I: V * I
        V = lambda P, I: P / I
        I = lambda P, V: P / V

class Optics:
    class Refraction:
        n = lambda c, v: c / v
        v = lambda c, n: c / n
        θ2 = lambda n1, n2, θ1: __import__('math').asin(n1 * __import__('math').sin(θ1) / n2)

class Quantum:
    class PhotonEnergy:
        E = lambda f, h=const.h: h * f
        f = lambda E, h=const.h: E / h
        λ = lambda E, h=const.h, c=const.c: h * c / E

# Примеры использования:
print("Сила тяжести:", Mechanics.Gravity.F(5, 10, 3))
print("Масса из закона Кулона:", Electromagnetism.Coulomb.q1(0.001, 1e-6, 0.1))
print("Энергия фотона:", Quantum.PhotonEnergy.E(6e14))
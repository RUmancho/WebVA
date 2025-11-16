import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import constants.physics as const


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
        Q = lambda m, c, dT: m * c * dT
        c = lambda Q, m, dT: Q / (m * dT)
        dT = lambda Q, m, c: Q / (m * c)

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

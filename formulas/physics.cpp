#include "physics.h"
#include <cmath>

namespace SpecificHeat {
    const int water = 4200;
    const int ice = 2100;
    const int water_steam = 2010;
    const int aluminum = 900;
    const int iron = 460;
    const int copper = 385;
    const int gold = 129;
    const int lead = 130;
    const int air = 1005;
    const int ethanol = 2440;
    const int granite = 790;
    const int glass = 840;
    const int wood = 1700;
    const int mercury = 140;
    const int hydrogen = 14300;
    const int oxygen = 920;
    const int concrete = 880;
    const int human_body = 3470;
    const int silver = 235;
    const int platinum = 133;
    const int zinc = 385;
    const int tin = 230;
    const int nickel = 440;
    const int titanium = 523;
    const int steel = 500;
    const int brass = 380;
    const int bronze = 380;
}

namespace Density {
    const double water = 1000.0;
    const double ice = 917.0;
    const double aluminum = 2700.0;
    const double iron = 7870.0;
    const double copper = 8960.0;
    const double gold = 19300.0;
    const double lead = 11340.0;
    const double mercury = 13590.0;
    const double air = 1.29;
    const double ethanol = 789.0;
    const double granite = 2700.0;
    const double glass = 2500.0;
    const double wood = 700.0;
    const double hydrogen = 0.0899;
    const double oxygen = 1.429;
    const double concrete = 2400.0;
    const double silver = 10500.0;
    const double platinum = 21450.0;
    const double zinc = 7140.0;
    const double tin = 7280.0;
    const double nickel = 8900.0;
    const double titanium = 4500.0;
    const double steel = 7850.0;
    const double brass = 8500.0;
    const double bronze = 8700.0;
    const double oil = 900.0;
    const double gasoline = 750.0;
    const double sea_water = 1025.0;
}

namespace Resistivity {
    const double silver = 1.59e-8;
    const double copper = 1.68e-8;
    const double gold = 2.44e-8;
    const double aluminum = 2.65e-8;
    const double tungsten = 5.60e-8;
    const double iron = 9.70e-8;
    const double platinum = 10.6e-8;
    const double lead = 22.0e-8;
    const double nichrome = 1.10e-6;
    const double carbon = 3.5e-5;
    const double germanium = 0.46;
    const double silicon = 640.0;
    const double glass = 1e12;
    const double rubber = 1e13;
    const double wood = 1e8;
}

namespace MeltingPoint {
    const double water = 0.0;
    const double aluminum = 660.3;
    const double iron = 1538.0;
    const double copper = 1085.0;
    const double gold = 1064.0;
    const double lead = 327.5;
    const double mercury = -38.8;
    const double silver = 961.8;
    const double platinum = 1768.0;
    const double zinc = 419.5;
    const double tin = 231.9;
    const double nickel = 1455.0;
    const double titanium = 1668.0;
    const double steel = 1370.0;
    const double tungsten = 3414.0;
}

namespace BoilingPoint {
    const double water = 100.0;
    const double aluminum = 2519.0;
    const double iron = 2862.0;
    const double copper = 2562.0;
    const double gold = 2856.0;
    const double lead = 1749.0;
    const double mercury = 356.7;
    const double silver = 2162.0;
    const double platinum = 3825.0;
    const double zinc = 907.0;
    const double tin = 2602.0;
    const double nickel = 2913.0;
    const double titanium = 3287.0;
    const double steel = 2750.0;
    const double tungsten = 5555.0;
}

namespace Constants {
    const double G = 6.67430e-11;
    const double k = 8.987551789e9;
    const double pi = 3.14159265358979323846;
    const double g = 9.80665;
    const double c = 299792458.0;
    const double h = 6.62607015e-34;
    const double R = 8.314462618;
}

namespace {
    double radians(double angle) noexcept {
        return angle * Constants::pi / 180.0;
    }
}

namespace Velocity {
    DLL double from_distance_time(double s, double t) noexcept {
        if (t == 0) return 0;
        return s / t;
    }
    
    DLL double from_acceleration_time(double v0, double a, double t) noexcept {
        return v0 + a * t;
    }
    
    DLL double from_acceleration_distance(double a, double s) noexcept {
        if (a < 0 || s < 0) return 0;
        return std::sqrt(2.0 * a * s);
    }
    
    // v = sqrt(v0^2 + 2*a*s)
    DLL double from_acceleration_distance_initial(double v0, double a, double s) noexcept {
        double v_squared = v0 * v0 + 2.0 * a * s;
        if (v_squared < 0) return 0;
        return std::sqrt(v_squared);
    }
    
    // v = sqrt(F*r/m) для центростремительной силы
    DLL double from_centripetal_force(double F, double r, double m) noexcept {
        if (m == 0 || r == 0) return 0;
        return std::sqrt(F * r / m);
    }
    
    // v = sqrt(2*E/m) для кинетической энергии
    DLL double from_kinetic_energy(double E, double m) noexcept {
        if (m == 0 || E < 0) return 0;
        return std::sqrt(2.0 * E / m);
    }
}

namespace Acceleration {
    // a = (v - v0) / t
    DLL double from_velocity_time(double v, double v0, double t) noexcept {
        if (t == 0) return 0;
        return (v - v0) / t;
    }
    
    // a = F / m
    DLL double from_force_mass(double F, double m) noexcept {
        if (m == 0) return 0;
        return F / m;
    }
    
    // a = (v^2 - v0^2) / (2*s)
    DLL double from_velocity_distance(double v, double v0, double s) noexcept {
        if (s == 0) return 0;
        return (v * v - v0 * v0) / (2.0 * s);
    }
    
    // a = 2*s / t^2 для начальной скорости 0
    DLL double from_distance_time(double s, double t) noexcept {
        if (t == 0) return 0;
        return 2.0 * s / (t * t);
    }
    
    // a = v^2 / r для центростремительного ускорения
    DLL double centripetal(double v, double r) noexcept {
        if (r == 0) return 0;
        return v * v / r;
    }
}

namespace Mass {
    // m = F / a
    DLL double from_force_acceleration(double F, double a) noexcept {
        if (a == 0) return 0;
        return F / a;
    }
    
    // m = p * V
    DLL double from_density_volume(double p, double V) noexcept {
        return p * V;
    }
    
    // m = E / (0.5 * v^2)
    DLL double from_kinetic_energy_velocity(double E, double v) noexcept {
        if (v == 0) return 0;
        return 2.0 * E / (v * v);
    }
    
    // m = E / (g * h)
    DLL double from_potential_energy_height(double E, double h, double g) noexcept {
        if (g == 0 || h == 0) return 0;
        return E / (g * h);
    }
    
    // m = F / g
    DLL double from_weight_gravity(double F, double g) noexcept {
        if (g == 0) return 0;
        return F / g;
    }
}

namespace Distance {
    // s = v * t
    DLL double from_velocity_time(double v, double t) noexcept {
        return v * t;
    }
    
    // s = v0*t + 0.5*a*t^2
    DLL double from_velocity_acceleration_time(double v0, double a, double t) noexcept {
        return v0 * t + 0.5 * a * t * t;
    }
    
    // s = (v^2 - v0^2) / (2*a)
    DLL double from_velocity_acceleration(double v, double v0, double a) noexcept {
        if (a == 0) return 0;
        return (v * v - v0 * v0) / (2.0 * a);
    }
    
    // s = E / F
    DLL double from_work_force(double E, double F) noexcept {
        if (F == 0) return 0;
        return E / F;
    }
}

namespace Time {
    // t = s / v
    DLL double from_distance_velocity(double s, double v) noexcept {
        if (v == 0) return 0;
        return s / v;
    }
    
    // t = (v - v0) / a
    DLL double from_velocity_acceleration(double v, double v0, double a) noexcept {
        if (a == 0) return 0;
        return (v - v0) / a;
    }
    
    // t = sqrt(2*s / a) для начальной скорости 0
    DLL double from_distance_acceleration(double s, double a) noexcept {
        if (a == 0 || s < 0) return 0;
        return std::sqrt(2.0 * s / a);
    }
    
    // t = W / P
    DLL double from_work_power(double W, double P) noexcept {
        if (P == 0) return 0;
        return W / P;
    }
}

namespace Force {
    DLL double gravity(double m, double g) noexcept {
        return m * g;
    }
    DLL double Newton_second_law(double m, double a) noexcept {
        return m * a;
    }
    DLL double universal_gravitation(double m1, double m2, double r, double G) noexcept {
        return G * (m1 * m2) / (r * r);
    }
    DLL double friction(double u, double N) noexcept {
        return u * N;
    }
    DLL double archimedes(double p, double V, double g) noexcept {
        return p * g * V;
    }
    DLL double coulomb(double q1, double q2, double r, double k) noexcept {
        return k * (q1 * q2) / (r * r);
    }
    DLL double lorentz(double q, double V, double B, double angle) noexcept {
        return q * V * B * std::sin(radians(angle));
    }
    DLL double ampere(double B, double I, double L, double angle) noexcept {
        return B * I * L * std::sin(radians(angle));
    }
    DLL double centripetal(double m, double V, double r) noexcept {
        return m * V * V / r;
    }
    DLL double pressure(double P, double S) noexcept {
        return P * S;
    }
    DLL double hydrostatic(double p, double h, double S, double g) noexcept {
        return p * g * h * S;
    }
}

namespace Energy {
    DLL double kinetic(double m, double V) noexcept {
        return 0.5 * m * V * V;
    }
    DLL double potential(double m, double h, double g) noexcept {
        return m * g * h;
    }
    DLL double elastic_potential(double k, double x) noexcept {
        return 0.5 * k * x * x;
    }
    DLL double rotational_kinetic(double I, double w) noexcept {
        return 0.5 * I * w * w;
    }
    DLL double capacitor(double C, double U) noexcept {
        return 0.5 * C * U * U;
    }
    DLL double thermal(double m, double c, double dt) noexcept {
        return m * c * dt;
    }
    DLL double combustion(double m, double q) noexcept {
        return m * q;
    }
    DLL double work_constant_force(double F, double s, double angle_degrees) noexcept {
        return F * s * std::cos(radians(angle_degrees));
    }
    DLL double work_variable_force_linear(double F_initial, double F_final, double s) noexcept {
        return 0.5 * (F_initial + F_final) * s;
    }
    DLL double work_gas_isobaric(double P, double dV) noexcept {
        return P * dV;
    }
    DLL double work_electric_field(double q, double U) noexcept {
        return q * U;
    }
    DLL double work_against_friction(double F_friction, double s) noexcept {
        return F_friction * s;
    }
    DLL double useful_work(double total_work, double efficiency) noexcept {
        return total_work * efficiency;
    }
    DLL double work_kinetic_energy_change(double m, double V_initial, double V_final) noexcept {
        return 0.5 * m * (V_final * V_final - V_initial * V_initial);
    }
    DLL double work_potential_energy_change(double m, double h_initial, double h_final, double g) noexcept {
        return m * g * (h_final - h_initial);
    }
    DLL double work_elastic_force(double k, double x_initial, double x_final) noexcept {
        return 0.5 * k * (x_final * x_final - x_initial * x_initial);
    }
    DLL double rest_energy(double m) noexcept {
        return m * Constants::c * Constants::c;
    }
    DLL double photon_energy(double frequency) noexcept {
        return Constants::h * frequency;
    }
    DLL double magnetic_energy(double L, double I) noexcept {
        return 0.5 * L * I * I;
    }
    DLL double chemical_energy(double moles, double bond_energy_per_mole) noexcept {
        return moles * bond_energy_per_mole;
    }
    DLL double activation_energy(double pre_exponential, double rate_constant, double T) noexcept {
        if (pre_exponential == 0 || rate_constant <= 0 || T <= 0) return 0;
        return -Constants::R * T * std::log(rate_constant / pre_exponential);
    }
}

namespace Height {
    // h = E / (m * g)
    DLL double from_potential_energy(double E, double m, double g) noexcept {
        if (m == 0 || g == 0) return 0;
        return E / (m * g);
    }
    
    // h = P / (p * g)
    DLL double from_pressure_density(double P, double p, double g) noexcept {
        if (p == 0 || g == 0) return 0;
        return P / (p * g);
    }
}

namespace Volume {
    // V = m / p
    DLL double from_mass_density(double m, double p) noexcept {
        if (p == 0) return 0;
        return m / p;
    }
    
    // V = F / (p * g) для силы Архимеда
    DLL double from_archimedes_force(double F, double p, double g) noexcept {
        if (p == 0 || g == 0) return 0;
        return F / (p * g);
    }
}

namespace Power {
    // P = W / t
    DLL double from_work_time(double W, double t) noexcept {
        if (t == 0) return 0;
        return W / t;
    }
    
    // P = F * v
    DLL double from_force_velocity(double F, double v) noexcept {
        return F * v;
    }
    
    // P = U * I
    DLL double from_voltage_current(double U, double I) noexcept {
        return U * I;
    }
    
    // P = I^2 * R
    DLL double from_current_resistance(double I, double R) noexcept {
        return I * I * R;
    }
    
    // P = U^2 / R
    DLL double from_voltage_resistance(double U, double R) noexcept {
        if (R == 0) return 0;
        return U * U / R;
    }
}

namespace PhysicsUtils {
    DLL double calculate_efficiency(double useful_work, double total_work) noexcept {
        if (total_work == 0) return 0;
        return useful_work / total_work;
    }
    
    DLL double calculate_power(double work, double time) noexcept {
        if (time == 0) return 0;
        return work / time;
    }
    
    DLL double calculate_work_from_power(double power, double time) noexcept {
        return power * time;
    }
}
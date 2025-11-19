#define DLL __declspec(dllexport)

namespace SpecificHeat {
    extern DLL const int water;
    extern DLL const int ice;
    extern DLL const int water_steam;
    extern DLL const int aluminum;
    extern DLL const int iron;
    extern DLL const int copper;
    extern DLL const int gold;
    extern DLL const int lead;
    extern DLL const int air;
    extern DLL const int ethanol;
    extern DLL const int granite;
    extern DLL const int glass;
    extern DLL const int wood;
    extern DLL const int mercury;
    extern DLL const int hydrogen;
    extern DLL const int oxygen;
    extern DLL const int concrete;
    extern DLL const int human_body;
}

namespace Constants {
    extern DLL const double G;
    extern DLL const double k;
    extern DLL const double pi;
    extern DLL const double g;
    extern DLL const double c;
    extern DLL const double h;
    extern DLL const double R;
}

namespace Force {
    DLL double gravity(double m, double g = Constants::g) noexcept;
    DLL double Newton_second_law(double m, double a) noexcept;
    DLL double universal_gravitation(double m1, double m2, double r, double G = Constants::G) noexcept;
    DLL double friction(double u, double N) noexcept;
    DLL double archimedes(double p, double V, double g = Constants::g) noexcept;
    DLL double coulomb(double q1, double q2, double r, double k = Constants::k) noexcept;
    DLL double lorentz(double q, double V, double B, double angle) noexcept;
    DLL double ampere(double B, double I, double L, double angle) noexcept;
    DLL double centripetal(double m, double V, double r) noexcept;
    DLL double pressure(double P, double S) noexcept;
    DLL double hydrostatic(double p, double h, double S, double g = Constants::g) noexcept;
}

namespace Energy {
    DLL double kinetic(double m, double V) noexcept;
    DLL double potential(double m, double h, double g = Constants::g) noexcept;
    DLL double elastic_potential(double k, double x) noexcept;
    DLL double rotational_kinetic(double I, double w) noexcept;
    DLL double capacitor(double C, double U) noexcept;
    DLL double thermal(double m, double c, double dt) noexcept;
    DLL double combustion(double m, double q) noexcept;
    DLL double work_constant_force(double F, double s, double angle_degrees = 0) noexcept;
    DLL double work_variable_force_linear(double F_initial, double F_final, double s) noexcept;
    DLL double work_gas_isobaric(double P, double dV) noexcept;
    DLL double work_electric_field(double q, double U) noexcept;
    DLL double work_against_friction(double F_friction, double s) noexcept;
    DLL double useful_work(double total_work, double efficiency) noexcept;
    DLL double work_kinetic_energy_change(double m, double V_initial, double V_final) noexcept;
    DLL double work_potential_energy_change(double m, double h_initial, double h_final, double g = Constants::g) noexcept;
    DLL double work_elastic_force(double k, double x_initial, double x_final) noexcept;
    DLL double rest_energy(double m) noexcept;
    DLL double photon_energy(double frequency) noexcept;
    DLL double magnetic_energy(double L, double I) noexcept;
    DLL double chemical_energy(double moles, double bond_energy_per_mole) noexcept;
    DLL double activation_energy(double pre_exponential, double rate_constant, double T) noexcept;
}

namespace PhysicsUtils {
    DLL double calculate_efficiency(double useful_work, double total_work) noexcept;
    DLL double calculate_power(double work, double time) noexcept;
    DLL double calculate_work_from_power(double power, double time) noexcept;
}

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
    extern DLL const int silver;
    extern DLL const int platinum;
    extern DLL const int zinc;
    extern DLL const int tin;
    extern DLL const int nickel;
    extern DLL const int titanium;
    extern DLL const int steel;
    extern DLL const int brass;
    extern DLL const int bronze;
}

namespace Density {
    extern DLL const double water;
    extern DLL const double ice;
    extern DLL const double aluminum;
    extern DLL const double iron;
    extern DLL const double copper;
    extern DLL const double gold;
    extern DLL const double lead;
    extern DLL const double mercury;
    extern DLL const double air;
    extern DLL const double ethanol;
    extern DLL const double granite;
    extern DLL const double glass;
    extern DLL const double wood;
    extern DLL const double hydrogen;
    extern DLL const double oxygen;
    extern DLL const double concrete;
    extern DLL const double silver;
    extern DLL const double platinum;
    extern DLL const double zinc;
    extern DLL const double tin;
    extern DLL const double nickel;
    extern DLL const double titanium;
    extern DLL const double steel;
    extern DLL const double brass;
    extern DLL const double bronze;
    extern DLL const double oil;
    extern DLL const double gasoline;
    extern DLL const double sea_water;
}

namespace Resistivity {
    extern DLL const double silver;
    extern DLL const double copper;
    extern DLL const double gold;
    extern DLL const double aluminum;
    extern DLL const double tungsten;
    extern DLL const double iron;
    extern DLL const double platinum;
    extern DLL const double lead;
    extern DLL const double nichrome;
    extern DLL const double carbon;
    extern DLL const double germanium;
    extern DLL const double silicon;
    extern DLL const double glass;
    extern DLL const double rubber;
    extern DLL const double wood;
}

namespace MeltingPoint {
    extern DLL const double water;
    extern DLL const double aluminum;
    extern DLL const double iron;
    extern DLL const double copper;
    extern DLL const double gold;
    extern DLL const double lead;
    extern DLL const double mercury;
    extern DLL const double silver;
    extern DLL const double platinum;
    extern DLL const double zinc;
    extern DLL const double tin;
    extern DLL const double nickel;
    extern DLL const double titanium;
    extern DLL const double steel;
    extern DLL const double tungsten;
}

namespace BoilingPoint {
    extern DLL const double water;
    extern DLL const double aluminum;
    extern DLL const double iron;
    extern DLL const double copper;
    extern DLL const double gold;
    extern DLL const double lead;
    extern DLL const double mercury;
    extern DLL const double silver;
    extern DLL const double platinum;
    extern DLL const double zinc;
    extern DLL const double tin;
    extern DLL const double nickel;
    extern DLL const double titanium;
    extern DLL const double steel;
    extern DLL const double tungsten;
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

namespace Velocity {
    DLL double from_distance_time(double s, double t) noexcept;
    DLL double from_acceleration_time(double v0, double a, double t) noexcept;
    DLL double from_acceleration_distance(double a, double s) noexcept;
    DLL double from_acceleration_distance_initial(double v0, double a, double s) noexcept;
    DLL double from_centripetal_force(double F, double r, double m) noexcept;
    DLL double from_kinetic_energy(double E, double m) noexcept;
}

namespace Acceleration {
    DLL double from_velocity_time(double v, double v0, double t) noexcept;
    DLL double from_force_mass(double F, double m) noexcept;
    DLL double from_velocity_distance(double v, double v0, double s) noexcept;
    DLL double from_distance_time(double s, double t) noexcept;
    DLL double centripetal(double v, double r) noexcept;
}

namespace Mass {
    DLL double from_force_acceleration(double F, double a) noexcept;
    DLL double from_density_volume(double p, double V) noexcept;
    DLL double from_kinetic_energy_velocity(double E, double v) noexcept;
    DLL double from_potential_energy_height(double E, double h, double g = Constants::g) noexcept;
    DLL double from_weight_gravity(double F, double g = Constants::g) noexcept;
}

namespace Distance {
    DLL double from_velocity_time(double v, double t) noexcept;
    DLL double from_velocity_acceleration_time(double v0, double a, double t) noexcept;
    DLL double from_velocity_acceleration(double v, double v0, double a) noexcept;
    DLL double from_work_force(double E, double F) noexcept;
}

namespace Time {
    DLL double from_distance_velocity(double s, double v) noexcept;
    DLL double from_velocity_acceleration(double v, double v0, double a) noexcept;
    DLL double from_distance_acceleration(double s, double a) noexcept;
    DLL double from_work_power(double W, double P) noexcept;
}

namespace Height {
    DLL double from_potential_energy(double E, double m, double g = Constants::g) noexcept;
    DLL double from_pressure_density(double P, double p, double g = Constants::g) noexcept;
}

namespace Volume {
    DLL double from_mass_density(double m, double p) noexcept;
    DLL double from_archimedes_force(double F, double p, double g = Constants::g) noexcept;
}

namespace Power {
    DLL double from_work_time(double W, double t) noexcept;
    DLL double from_force_velocity(double F, double v) noexcept;
    DLL double from_voltage_current(double U, double I) noexcept;
    DLL double from_current_resistance(double I, double R) noexcept;
    DLL double from_voltage_resistance(double U, double R) noexcept;
}

namespace PhysicsUtils {
    DLL double calculate_efficiency(double useful_work, double total_work) noexcept;
    DLL double calculate_power(double work, double time) noexcept;
    DLL double calculate_work_from_power(double power, double time) noexcept;
}

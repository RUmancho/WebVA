#define DLL __declspec(dllexport)

namespace Quadratic {
    DLL double discriminant(double a, double b, double c) noexcept;
    DLL double vertex_x(double a, double b) noexcept;
    DLL double vertex_y(double a, double b, double c) noexcept;
}

namespace Linear {
    DLL double solve(double a, double b) noexcept;
    DLL double slope(double x1, double y1, double x2, double y2) noexcept;
    DLL double y_intercept(double x, double y, double slope) noexcept;
    DLL double evaluate(double x, double slope, double intercept) noexcept;
}

namespace Arithmetic {
    DLL double sum(double a, double b) noexcept;
    DLL double difference(double a, double b) noexcept;
    DLL double product(double a, double b) noexcept;
    DLL double quotient(double a, double b) noexcept;
    DLL double average(double a, double b) noexcept;
    DLL double average(double a, double b, double c) noexcept;
    DLL double average(double values[], int count) noexcept;
}

namespace Geometric {
    DLL double geometric_mean(double a, double b) noexcept;
    DLL double geometric_mean(double a, double b, double c) noexcept;
    DLL double geometric_mean(double values[], int count) noexcept;
}

namespace Logarithm {
    DLL double natural_log(double x) noexcept;
    DLL double log_base_10(double x) noexcept;
    DLL double log_base(double x, double base) noexcept;
    DLL double power(double base, double exponent) noexcept;
}

namespace Exponential {
    DLL double exp(double x) noexcept;
    DLL double exp_base(double base, double exponent) noexcept;
    DLL double compound_interest(double principal, double rate, double time, int periods) noexcept;
    DLL double continuous_compound(double principal, double rate, double time) noexcept;
}

namespace Factorial {
    DLL long long calculate(int n) noexcept;
}

namespace Permutation {
    DLL long long calculate(int n, int r) noexcept;
}

namespace Combination {
    DLL long long calculate(int n, int r) noexcept;
}

namespace Trigonometry {
    DLL double sin_degrees(double angle) noexcept;
    DLL double cos_degrees(double angle) noexcept;
    DLL double tan_degrees(double angle) noexcept;
    DLL double asin_degrees(double value) noexcept;
    DLL double acos_degrees(double value) noexcept;
    DLL double atan_degrees(double value) noexcept;
    DLL double atan2_degrees(double y, double x) noexcept;
}

namespace Statistics {
    DLL double mean(double values[], int count) noexcept;
    DLL double variance(double values[], int count) noexcept;
    DLL double standard_deviation(double values[], int count) noexcept;
    DLL double min(double values[], int count) noexcept;
    DLL double max(double values[], int count) noexcept;
}

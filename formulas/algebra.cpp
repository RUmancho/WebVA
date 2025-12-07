#include "algebra.h"
#include <cmath>

namespace Quadratic {
    DLL double discriminant(double a, double b, double c) noexcept {
        return b * b - 4.0 * a * c;
    }
    
    DLL double vertex_x(double a, double b) noexcept {
        if (a == 0) return 0;
        return -b / (2.0 * a);
    }
    
    DLL double vertex_y(double a, double b, double c) noexcept {
        double x = vertex_x(a, b);
        return a * x * x + b * x + c;
    }
}

namespace Linear {
    DLL double solve(double a, double b) noexcept {
        if (a == 0) return 0;
        return -b / a;
    }
    
    DLL double slope(double x1, double y1, double x2, double y2) noexcept {
        if (x2 == x1) return 0;
        return (y2 - y1) / (x2 - x1);
    }
    
    DLL double y_intercept(double x, double y, double slope) noexcept {
        return y - slope * x;
    }
    
    DLL double evaluate(double x, double slope, double intercept) noexcept {
        return slope * x + intercept;
    }
}

namespace Arithmetic {
    DLL double sum(double a, double b) noexcept {
        return a + b;
    }
    
    DLL double difference(double a, double b) noexcept {
        return a - b;
    }
    
    DLL double product(double a, double b) noexcept {
        return a * b;
    }
    
    DLL double quotient(double a, double b) noexcept {
        if (b == 0) return 0;
        return a / b;
    }
    
    DLL double average(double a, double b) noexcept {
        return (a + b) / 2.0;
    }
    
    DLL double average(double a, double b, double c) noexcept {
        return (a + b + c) / 3.0;
    }
    
    DLL double average(double values[], int count) noexcept {
        if (count == 0) return 0;
        double sum = 0;
        for (int i = 0; i < count; ++i) {
            sum += values[i];
        }
        return sum / count;
    }
}

namespace Geometric {
    DLL double geometric_mean(double a, double b) noexcept {
        if (a < 0 || b < 0) return 0;
        return std::sqrt(a * b);
    }
    
    DLL double geometric_mean(double a, double b, double c) noexcept {
        if (a < 0 || b < 0 || c < 0) return 0;
        return std::cbrt(a * b * c);
    }
    
    DLL double geometric_mean(double values[], int count) noexcept {
        if (count == 0) return 0;
        double product = 1.0;
        for (int i = 0; i < count; ++i) {
            if (values[i] < 0) return 0;
            product *= values[i];
        }
        return std::pow(product, 1.0 / count);
    }
}

namespace Logarithm {
    DLL double natural_log(double x) noexcept {
        if (x <= 0) return 0;
        return std::log(x);
    }
    
    DLL double log_base_10(double x) noexcept {
        if (x <= 0) return 0;
        return std::log10(x);
    }
    
    DLL double log_base(double x, double base) noexcept {
        if (x <= 0 || base <= 0 || base == 1) return 0;
        return std::log(x) / std::log(base);
    }
    
    DLL double power(double base, double exponent) noexcept {
        return std::pow(base, exponent);
    }
}

namespace Exponential {
    DLL double exp(double x) noexcept {
        return std::exp(x);
    }
    
    DLL double exp_base(double base, double exponent) noexcept {
        return std::pow(base, exponent);
    }
    
    DLL double compound_interest(double principal, double rate, double time, int periods) noexcept {
        if (periods == 0) return principal;
        return principal * std::pow(1.0 + rate / periods, periods * time);
    }
    
    DLL double continuous_compound(double principal, double rate, double time) noexcept {
        return principal * std::exp(rate * time);
    }
}

namespace Factorial {
    DLL long long calculate(int n) noexcept {
        if (n < 0) return 0;
        if (n == 0 || n == 1) return 1;
        long long result = 1;
        for (int i = 2; i <= n; ++i) {
            result *= i;
        }
        return result;
    }
}

namespace Permutation {
    DLL long long calculate(int n, int r) noexcept {
        if (n < 0 || r < 0 || r > n) return 0;
        if (r == 0) return 1;
        long long result = 1;
        for (int i = 0; i < r; ++i) {
            result *= (n - i);
        }
        return result;
    }
}

namespace Combination {
    DLL long long calculate(int n, int r) noexcept {
        if (n < 0 || r < 0 || r > n) return 0;
        if (r > n - r) r = n - r;
        if (r == 0) return 1;
        long long result = 1;
        for (int i = 0; i < r; ++i) {
            result = result * (n - i) / (i + 1);
        }
        return result;
    }
}

namespace Trigonometry {
    DLL double sin_degrees(double angle) noexcept {
        return std::sin(angle * 3.14159265358979323846 / 180.0);
    }
    
    DLL double cos_degrees(double angle) noexcept {
        return std::cos(angle * 3.14159265358979323846 / 180.0);
    }
    
    DLL double tan_degrees(double angle) noexcept {
        return std::tan(angle * 3.14159265358979323846 / 180.0);
    }
    
    DLL double asin_degrees(double value) noexcept {
        return std::asin(value) * 180.0 / 3.14159265358979323846;
    }
    
    DLL double acos_degrees(double value) noexcept {
        return std::acos(value) * 180.0 / 3.14159265358979323846;
    }
    
    DLL double atan_degrees(double value) noexcept {
        return std::atan(value) * 180.0 / 3.14159265358979323846;
    }
    
    DLL double atan2_degrees(double y, double x) noexcept {
        return std::atan2(y, x) * 180.0 / 3.14159265358979323846;
    }
}

namespace Statistics {
    DLL double mean(double values[], int count) noexcept {
        if (count == 0) return 0;
        double sum = 0;
        for (int i = 0; i < count; ++i) {
            sum += values[i];
        }
        return sum / count;
    }
    
    DLL double variance(double values[], int count) noexcept {
        if (count == 0) return 0;
        double mean_val = mean(values, count);
        double sum_squared_diff = 0;
        for (int i = 0; i < count; ++i) {
            double diff = values[i] - mean_val;
            sum_squared_diff += diff * diff;
        }
        return sum_squared_diff / count;
    }
    
    DLL double standard_deviation(double values[], int count) noexcept {
        return std::sqrt(variance(values, count));
    }
    
    DLL double min(double values[], int count) noexcept {
        if (count == 0) return 0;
        double min_val = values[0];
        for (int i = 1; i < count; ++i) {
            if (values[i] < min_val) min_val = values[i];
        }
        return min_val;
    }
    
    DLL double max(double values[], int count) noexcept {
        if (count == 0) return 0;
        double max_val = values[0];
        for (int i = 1; i < count; ++i) {
            if (values[i] > max_val) max_val = values[i];
        }
        return max_val;
    }
}


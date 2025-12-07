#include "geometry.h"
#include <cmath>

namespace Constants {
    const double PI = 3.141592;
}

namespace Circle {
    DLL double area(double radius) noexcept {
        return Constants::PI * radius * radius;
    }
    
    DLL double circumference(double radius) noexcept {
        return 2.0 * Constants::PI * radius;
    }
    
    DLL double diameter(double radius) noexcept {
        return 2.0 * radius;
    }
    
    DLL double radius_from_area(double area) noexcept {
        if (area < 0) return 0;
        return std::sqrt(area / Constants::PI);
    }
    
    DLL double radius_from_circumference(double circumference) noexcept {
        if (circumference <= 0) return 0;
        return circumference / (2.0 * Constants::PI);
    }
    
    DLL double sector_area(double radius, double angle_degrees) noexcept {
        return (angle_degrees / 360.0) * Constants::PI * radius * radius;
    }
    
    DLL double arc_length(double radius, double angle_degrees) noexcept {
        return (angle_degrees / 360.0) * 2.0 * Constants::PI * radius;
    }
}

namespace Rectangle {
    DLL double area(double length, double width) noexcept {
        return length * width;
    }
    
    DLL double perimeter(double length, double width) noexcept {
        return 2.0 * (length + width);
    }
    
    DLL double diagonal(double length, double width) noexcept {
        return std::sqrt(length * length + width * width);
    }
    
    DLL double length_from_area_width(double area, double width) noexcept {
        if (width == 0) return 0;
        return area / width;
    }
    
    DLL double width_from_area_length(double area, double length) noexcept {
        if (length == 0) return 0;
        return area / length;
    }
}

namespace Square {
    DLL double area(double side) noexcept {
        return side * side;
    }
    
    DLL double perimeter(double side) noexcept {
        return 4.0 * side;
    }
    
    DLL double diagonal(double side) noexcept {
        return side * std::sqrt(2.0);
    }
    
    DLL double side_from_area(double area) noexcept {
        if (area < 0) return 0;
        return std::sqrt(area);
    }
    
    DLL double side_from_diagonal(double diagonal) noexcept {
        if (diagonal <= 0) return 0;
        return diagonal / std::sqrt(2.0);
    }
}

namespace Triangle {
    DLL double area_base_height(double base, double height) noexcept {
        return 0.5 * base * height;
    }
    
    DLL double area_heron(double a, double b, double c) noexcept {
        double s = (a + b + c) / 2.0;
        if (s <= 0 || s <= a || s <= b || s <= c) return 0;
        return std::sqrt(s * (s - a) * (s - b) * (s - c));
    }
    
    DLL double area_sides_angle(double a, double b, double angle_degrees) noexcept {
        double angle_rad = angle_degrees * Constants::PI / 180.0;
        return 0.5 * a * b * std::sin(angle_rad);
    }
    
    DLL double perimeter(double a, double b, double c) noexcept {
        return a + b + c;
    }
    
    DLL double height_from_area_base(double area, double base) noexcept {
        if (base == 0) return 0;
        return 2.0 * area / base;
    }
    
    DLL bool is_valid(double a, double b, double c) noexcept {
        return (a + b > c) && (a + c > b) && (b + c > a);
    }
}

namespace RightTriangle {
    DLL double hypotenuse(double a, double b) noexcept {
        return std::sqrt(a * a + b * b);
    }
    
    DLL double leg_from_hypotenuse_leg(double hypotenuse, double leg) noexcept {
        double leg_squared = hypotenuse * hypotenuse - leg * leg;
        if (leg_squared < 0) return 0;
        return std::sqrt(leg_squared);
    }
    
    DLL double area(double a, double b) noexcept {
        return 0.5 * a * b;
    }
    
    DLL double perimeter(double a, double b) noexcept {
        double c = hypotenuse(a, b);
        return a + b + c;
    }
}

namespace Trapezoid {
    DLL double area(double base1, double base2, double height) noexcept {
        return 0.5 * (base1 + base2) * height;
    }
    
    DLL double perimeter(double base1, double base2, double side1, double side2) noexcept {
        return base1 + base2 + side1 + side2;
    }
    
    DLL double height_from_area_bases(double area, double base1, double base2) noexcept {
        if (base1 + base2 == 0) return 0;
        return 2.0 * area / (base1 + base2);
    }
}

namespace Parallelogram {
    DLL double area_base_height(double base, double height) noexcept {
        return base * height;
    }
    
    DLL double area_sides_angle(double a, double b, double angle_degrees) noexcept {
        double angle_rad = angle_degrees * Constants::PI / 180.0;
        return a * b * std::sin(angle_rad);
    }
    
    DLL double perimeter(double a, double b) noexcept {
        return 2.0 * (a + b);
    }
    
    DLL double height_from_area_base(double area, double base) noexcept {
        if (base == 0) return 0;
        return area / base;
    }
}

namespace Rhombus {
    DLL double area_diagonals(double d1, double d2) noexcept {
        return 0.5 * d1 * d2;
    }
    
    DLL double area_side_height(double side, double height) noexcept {
        return side * height;
    }
    
    DLL double area_side_angle(double side, double angle_degrees) noexcept {
        double angle_rad = angle_degrees * Constants::PI / 180.0;
        return side * side * std::sin(angle_rad);
    }
    
    DLL double perimeter(double side) noexcept {
        return 4.0 * side;
    }
}

namespace Ellipse {
    DLL double area(double a, double b) noexcept {
        return Constants::PI * a * b;
    }
    
    DLL double circumference_approximate(double a, double b) noexcept {
        double h = std::pow((a - b) / (a + b), 2);
        return Constants::PI * (a + b) * (1.0 + 3.0 * h / (10.0 + std::sqrt(4.0 - 3.0 * h)));
    }
    
    DLL double eccentricity(double a, double b) noexcept {
        if (a == 0) return 0;
        double e_squared = 1.0 - (b * b) / (a * a);
        if (e_squared < 0) return 0;
        return std::sqrt(e_squared);
    }
}

namespace Sphere {
    DLL double volume(double radius) noexcept {
        return (4.0 / 3.0) * Constants::PI * radius * radius * radius;
    }
    
    DLL double surface_area(double radius) noexcept {
        return 4.0 * Constants::PI * radius * radius;
    }
    
    DLL double radius_from_volume(double volume) noexcept {
        if (volume < 0) return 0;
        return std::cbrt(3.0 * volume / (4.0 * Constants::PI));
    }
    
    DLL double radius_from_surface_area(double surface_area) noexcept {
        if (surface_area < 0) return 0;
        return std::sqrt(surface_area / (4.0 * Constants::PI));
    }
}

namespace Cylinder {
    DLL double volume(double radius, double height) noexcept {
        return Constants::PI * radius * radius * height;
    }
    
    DLL double lateral_surface_area(double radius, double height) noexcept {
        return 2.0 * Constants::PI * radius * height;
    }
    
    DLL double total_surface_area(double radius, double height) noexcept {
        return 2.0 * Constants::PI * radius * (radius + height);
    }
    
    DLL double height_from_volume_radius(double volume, double radius) noexcept {
        if (radius == 0) return 0;
        return volume / (Constants::PI * radius * radius);
    }
}

namespace Cone {
    DLL double volume(double radius, double height) noexcept {
        return (1.0 / 3.0) * Constants::PI * radius * radius * height;
    }
    
    DLL double lateral_surface_area(double radius, double slant_height) noexcept {
        return Constants::PI * radius * slant_height;
    }
    
    DLL double total_surface_area(double radius, double slant_height) noexcept {
        return Constants::PI * radius * (radius + slant_height);
    }
    
    DLL double slant_height(double radius, double height) noexcept {
        return std::sqrt(radius * radius + height * height);
    }
    
    DLL double height_from_volume_radius(double volume, double radius) noexcept {
        if (radius == 0) return 0;
        return 3.0 * volume / (Constants::PI * radius * radius);
    }
}

namespace RectangularPrism {
    DLL double volume(double length, double width, double height) noexcept {
        return length * width * height;
    }
    
    DLL double surface_area(double length, double width, double height) noexcept {
        return 2.0 * (length * width + length * height + width * height);
    }
    
    DLL double diagonal(double length, double width, double height) noexcept {
        return std::sqrt(length * length + width * width + height * height);
    }
    
    DLL double height_from_volume_length_width(double volume, double length, double width) noexcept {
        if (length == 0 || width == 0) return 0;
        return volume / (length * width);
    }
}

namespace Cube {
    DLL double volume(double side) noexcept {
        return side * side * side;
    }
    
    DLL double surface_area(double side) noexcept {
        return 6.0 * side * side;
    }
    
    DLL double diagonal(double side) noexcept {
        return side * std::sqrt(3.0);
    }
    
    DLL double side_from_volume(double volume) noexcept {
        if (volume < 0) return 0;
        return std::cbrt(volume);
    }
    
    DLL double side_from_surface_area(double surface_area) noexcept {
        if (surface_area < 0) return 0;
        return std::sqrt(surface_area / 6.0);
    }
}

namespace Pyramid {
    DLL double volume_rectangular_base(double length, double width, double height) noexcept {
        return (1.0 / 3.0) * length * width * height;
    }
    
    DLL double volume_square_base(double base_side, double height) noexcept {
        return (1.0 / 3.0) * base_side * base_side * height;
    }
    
    DLL double volume_triangular_base(double base_area, double height) noexcept {
        return (1.0 / 3.0) * base_area * height;
    }
    
    DLL double height_from_volume_base_area(double volume, double base_area) noexcept {
        if (base_area == 0) return 0;
        return 3.0 * volume / base_area;
    }
}

namespace Polygon {
    DLL double interior_angle_sum(int n) noexcept {
        if (n < 3) return 0;
        return (n - 2) * 180.0;
    }
    
    DLL double interior_angle_regular(int n) noexcept {
        if (n < 3) return 0;
        return ((n - 2) * 180.0) / n;
    }
    
    DLL double exterior_angle_sum(int n) noexcept {
        (void)n;
        return 360.0;
    }
    
    DLL double exterior_angle_regular(int n) noexcept {
        if (n == 0) return 0;
        return 360.0 / n;
    }
}

namespace Distance {
    DLL double point_to_point_2d(double x1, double y1, double x2, double y2) noexcept {
        double dx = x2 - x1;
        double dy = y2 - y1;
        return std::sqrt(dx * dx + dy * dy);
    }
    
    DLL double point_to_point_3d(double x1, double y1, double z1, double x2, double y2, double z2) noexcept {
        double dx = x2 - x1;
        double dy = y2 - y1;
        double dz = z2 - z1;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
    
    DLL double point_to_line_2d(double px, double py, double x1, double y1, double x2, double y2) noexcept {
        double A = y2 - y1;
        double B = x1 - x2;
        double C = x2 * y1 - x1 * y2;
        double denominator = std::sqrt(A * A + B * B);
        if (denominator == 0) return 0;
        return std::abs(A * px + B * py + C) / denominator;
    }
}


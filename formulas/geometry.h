#define DLL __declspec(dllexport)

namespace Circle {
    DLL double area(double radius) noexcept;
    DLL double circumference(double radius) noexcept;
    DLL double diameter(double radius) noexcept;
    DLL double radius_from_area(double area) noexcept;
    DLL double radius_from_circumference(double circumference) noexcept;
    DLL double sector_area(double radius, double angle_degrees) noexcept;
    DLL double arc_length(double radius, double angle_degrees) noexcept;
}

namespace Rectangle {
    DLL double area(double length, double width) noexcept;
    DLL double perimeter(double length, double width) noexcept;
    DLL double diagonal(double length, double width) noexcept;
    DLL double length_from_area_width(double area, double width) noexcept;
    DLL double width_from_area_length(double area, double length) noexcept;
}

namespace Square {
    DLL double area(double side) noexcept;
    DLL double perimeter(double side) noexcept;
    DLL double diagonal(double side) noexcept;
    DLL double side_from_area(double area) noexcept;
    DLL double side_from_diagonal(double diagonal) noexcept;
}

namespace Triangle {
    DLL double area_base_height(double base, double height) noexcept;
    DLL double area_heron(double a, double b, double c) noexcept;
    DLL double area_sides_angle(double a, double b, double angle_degrees) noexcept;
    DLL double perimeter(double a, double b, double c) noexcept;
    DLL double height_from_area_base(double area, double base) noexcept;
    DLL bool is_valid(double a, double b, double c) noexcept;
}

namespace RightTriangle {
    DLL double hypotenuse(double a, double b) noexcept;
    DLL double leg_from_hypotenuse_leg(double hypotenuse, double leg) noexcept;
    DLL double area(double a, double b) noexcept;
    DLL double perimeter(double a, double b) noexcept;
}

namespace Trapezoid {
    DLL double area(double base1, double base2, double height) noexcept;
    DLL double perimeter(double base1, double base2, double side1, double side2) noexcept;
    DLL double height_from_area_bases(double area, double base1, double base2) noexcept;
}

namespace Parallelogram {
    DLL double area_base_height(double base, double height) noexcept;
    DLL double area_sides_angle(double a, double b, double angle_degrees) noexcept;
    DLL double perimeter(double a, double b) noexcept;
    DLL double height_from_area_base(double area, double base) noexcept;
}

namespace Rhombus {
    DLL double area_diagonals(double d1, double d2) noexcept;
    DLL double area_side_height(double side, double height) noexcept;
    DLL double area_side_angle(double side, double angle_degrees) noexcept;
    DLL double perimeter(double side) noexcept;
}

namespace Ellipse {
    DLL double area(double a, double b) noexcept;
    DLL double circumference_approximate(double a, double b) noexcept;
    DLL double eccentricity(double a, double b) noexcept;
}

namespace Sphere {
    DLL double volume(double radius) noexcept;
    DLL double surface_area(double radius) noexcept;
    DLL double radius_from_volume(double volume) noexcept;
    DLL double radius_from_surface_area(double surface_area) noexcept;
}

namespace Cylinder {
    DLL double volume(double radius, double height) noexcept;
    DLL double lateral_surface_area(double radius, double height) noexcept;
    DLL double total_surface_area(double radius, double height) noexcept;
    DLL double height_from_volume_radius(double volume, double radius) noexcept;
}

namespace Cone {
    DLL double volume(double radius, double height) noexcept;
    DLL double lateral_surface_area(double radius, double slant_height) noexcept;
    DLL double total_surface_area(double radius, double slant_height) noexcept;
    DLL double slant_height(double radius, double height) noexcept;
    DLL double height_from_volume_radius(double volume, double radius) noexcept;
}

namespace RectangularPrism {
    DLL double volume(double length, double width, double height) noexcept;
    DLL double surface_area(double length, double width, double height) noexcept;
    DLL double diagonal(double length, double width, double height) noexcept;
    DLL double height_from_volume_length_width(double volume, double length, double width) noexcept;
}

namespace Cube {
    DLL double volume(double side) noexcept;
    DLL double surface_area(double side) noexcept;
    DLL double diagonal(double side) noexcept;
    DLL double side_from_volume(double volume) noexcept;
    DLL double side_from_surface_area(double surface_area) noexcept;
}

namespace Pyramid {
    DLL double volume_rectangular_base(double length, double width, double height) noexcept;
    DLL double volume_square_base(double base_side, double height) noexcept;
    DLL double volume_triangular_base(double base_area, double height) noexcept;
    DLL double height_from_volume_base_area(double volume, double base_area) noexcept;
}

namespace Polygon {
    DLL double interior_angle_sum(int n) noexcept;
    DLL double interior_angle_regular(int n) noexcept;
    DLL double exterior_angle_sum(int n) noexcept;
    DLL double exterior_angle_regular(int n) noexcept;
}

namespace Distance {
    DLL double point_to_point_2d(double x1, double y1, double x2, double y2) noexcept;
    DLL double point_to_point_3d(double x1, double y1, double z1, double x2, double y2, double z2) noexcept;
    DLL double point_to_line_2d(double px, double py, double x1, double y1, double x2, double y2) noexcept;
}


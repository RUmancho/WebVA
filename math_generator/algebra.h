enum DifficultyLevel {
    DIFFICULTY_EASY = 1,
    DIFFICULTY_MEDIUM = 2,
    DIFFICULTY_HARD = 3
};

char* equation_linear(int difficulty_level);
char* equation_quadratic(int difficulty_level);
char* equation_exponential(int difficulty_level);
char* inequality_linear(int difficulty_level);
char* inequality_quadratic(int difficulty_level);
void free_string(char* string_ptr);
int random_int(int min_value, int max_value);
double random_double(double min_value, double max_value);
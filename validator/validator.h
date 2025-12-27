bool is_ascii_printable(const char16_t* str); // проверка ASCII
bool is_name(const char16_t* str); //Валидация имени
bool is_email(const wchar_t* str); //Валидация Email
bool is_password(const char16_t* str, int32_t min_len); //Валидация пароля
bool is_ru_class(const char16_t* str); //Проверка школьного класса
bool is_ru_school(const char16_t* str); //Валидация названия школы
bool is_ru_city(const char16_t* str); //Валидация города РФ
int32_t get_string_length(const char16_t* str); //длина строки char16_t
from __future__ import annotations

import re

_NAME_RE = re.compile(r"^[ A-Za-zА-Яа-яЁё\-]+$")
_LETTER_RE = re.compile(r"[A-Za-zА-Яа-яЁё]")
_DIGIT_RE = re.compile(r"\d")
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
_CLASS_RE = re.compile(r"^(?:0?[1-9]|1[01])[А-Яа-яЁё]$")
_CITY_RE = re.compile(r"^[А-Яа-яЁё]+(?:[ \-][А-Яа-яЁё]+)*\.?$")
_SCHOOL_RE = re.compile(r"^[A-Za-zА-Яа-яЁё0-9 №\-]+$")


def is_name(line: str) -> bool:
    """Letters, spaces and hyphens; at least one letter."""
    try:
        if not line:
            return False
        return bool(_NAME_RE.fullmatch(line) and _LETTER_RE.search(line))
    except Exception as e:
        print(f"[ValidatorFallback] is_name error: {e}")
        return False


def is_email(line: str) -> bool:
    """ASCII email with a domain and a 2+ letter TLD."""
    try:
        if not line:
            return False
        return bool(_EMAIL_RE.fullmatch(line))
    except Exception as e:
        print(f"[ValidatorFallback] is_email error: {e}")
        return False


def is_password(line: str, min_len: int = 6) -> bool:
    """At least min_len characters, with letters and digits."""
    try:
        if not line or min_len < 0:
            return False
        if len(line) < min_len:
            return False
        return bool(_LETTER_RE.search(line) and _DIGIT_RE.search(line))
    except Exception as e:
        print(f"[ValidatorFallback] is_password error: {e}")
        return False


def is_ru_class(line: str) -> bool:
    """School class 1-11 plus one Cyrillic letter, e.g. 10Б."""
    try:
        if not line:
            return False
        return bool(_CLASS_RE.fullmatch(line))
    except Exception as e:
        print(f"[ValidatorFallback] is_ru_class error: {e}")
        return False


def is_ru_school(line: str) -> bool:
    """School name, at least 3 characters, must contain a letter."""
    try:
        if not line or len(line) < 3:
            return False
        if not _SCHOOL_RE.fullmatch(line):
            return False
        return bool(_LETTER_RE.search(line))
    except Exception as e:
        print(f"[ValidatorFallback] is_ru_school error: {e}")
        return False


def is_ru_city(line: str) -> bool:
    """Cyrillic city name, spaces/hyphens allowed, min 2 letters."""
    try:
        if not line or len(line) < 2:
            return False
        return bool(_CITY_RE.fullmatch(line))
    except Exception as e:
        print(f"[ValidatorFallback] is_ru_city error: {e}")
        return False

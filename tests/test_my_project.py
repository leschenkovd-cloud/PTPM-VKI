import unittest
import sys
import os

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from my_project import validate


class TestLoginValidation(unittest.TestCase):
    """Тесты валидации логина"""
    def test_empty_login_returns_error(self):
        """Пустой логин должен отклоняться"""
        is_ok, msg = validate("", "Пароль123!", "Пароль123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Логин пуст")

    def test_valid_string_login_accepted(self):
        """Валидный строковый логин (минимум 5 символов) должен приниматься"""
        is_ok, msg = validate("valid_user_1", "Пароль123!", "Пароль123!")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")

    def test_valid_email_login_accepted(self):
        """Валидный email логин должен приниматься"""
        is_ok, msg = validate("user@example.com", "Пароль123!", "Пароль123!")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")

    def test_valid_phone_login_accepted(self):
        """Валидный телефон в формате +X-XXX-XXX-XXXX должен приниматься"""
        is_ok, msg = validate("+7-999-123-4567", "Пароль123!", "Пароль123!")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")

    def test_blacklisted_login_admin_rejected(self):
        """Логин 'admin' должен отклоняться (черный список)"""
        is_ok, msg = validate("admin", "Пароль123!", "Пароль123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Логин в черном списке")

    def test_blacklisted_login_root_rejected(self):
        """Логин 'root' должен отклоняться (черный список)"""
        is_ok, msg = validate("root", "Пароль123!", "Пароль123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Логин в черном списке")

    def test_blacklisted_login_case_insensitive(self):
        """Логин 'ADMIN' (верхний регистр) должен отклоняться"""
        is_ok, msg = validate("ADMIN", "Пароль123!", "Пароль123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Логин в черном списке")

    def test_invalid_login_format_rejected(self):
        """Логин с недопустимыми символами должен отклоняться"""
        is_ok, msg = validate("user@name!", "Пароль123!", "Пароль123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Неверный формат логина")

    def test_short_login_rejected(self):
        """Логин короче 5 символов (для строкового формата) должен отклоняться"""
        is_ok, msg = validate("user", "Пароль123!", "Пароль123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Неверный формат логина")


class TestPasswordValidation(unittest.TestCase):
    """Тесты валидации пароля"""

    def test_empty_password_returns_error(self):
        """Пустой пароль должен отклоняться"""
        is_ok, msg = validate("valid_user_1", "", "")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Пароль пуст")

    def test_short_password_rejected(self):
        """Пароль короче 7 символов должен отклоняться"""
        is_ok, msg = validate("valid_user_1", "Пар1!", "Пар1!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Пароль короче 7 символов")

    def test_password_with_latin_chars_rejected(self):
        """Пароль с латинскими буквами должен отклоняться"""
        is_ok, msg = validate("valid_user_1", "Password123!", "Password123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Пароль содержит недопустимые символы (например, латиницу)")

    def test_password_without_uppercase_cyrillic_rejected(self):
        """Пароль без заглавной кириллицы должен отклоняться"""
        is_ok, msg = validate("valid_user_1", "пароль123!", "пароль123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Нет заглавной кириллицы")

    def test_password_without_lowercase_cyrillic_rejected(self):
        """Пароль без строчной кириллицы должен отклоняться"""
        is_ok, msg = validate("valid_user_1", "ПАРОЛЬ123!", "ПАРОЛЬ123!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Нет строчной кириллицы")

    def test_password_without_digit_rejected(self):
        """Пароль без цифры должен отклоняться"""
        is_ok, msg = validate("valid_user_1", "Пароль!!!", "Пароль!!!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Нет цифры")

    def test_password_without_special_char_rejected(self):
        """Пароль без спецсимвола должен отклоняться"""
        is_ok, msg = validate("valid_user_1", "Пароль123", "Пароль123")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Нет спецсимвола")

    def test_password_with_all_requirements_accepted(self):
        """Пароль со всеми требованиями должен приниматься"""
        is_ok, msg = validate("valid_user_1", "Пароль123!", "Пароль123!")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")

    def test_password_min_length_accepted(self):
        """Пароль ровно 7 символов должен приниматься (если все требования выполнены)"""
        # Минимальный пароль: 1 заглавная + 1 строчная + 1 цифра + 1 спецсимвол = минимум 4
        # Но нужно 7 символов, так что добавим еще кириллицы
        is_ok, msg = validate("valid_user_1", "Пар1оль!", "Пар1оль!")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")


class TestPasswordMatching(unittest.TestCase):
    """Тесты совпадения паролей"""

    def test_mismatched_passwords_rejected(self):
        """Несовпадающие пароли должны отклоняться"""
        is_ok, msg = validate("valid_user_1", "Пароль123!", "Пароль124!")
        self.assertFalse(is_ok)
        self.assertEqual(msg, "Пароли не совпадают")

    def test_matched_passwords_accepted(self):
        """Совпадающие пароли должны приниматься (при прочих валидных условиях)"""
        is_ok, msg = validate("valid_user_1", "Пароль123!", "Пароль123!")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""

    def test_login_with_spaces_stripped(self):
        """Логин с пробелами должен обрезаться"""
        is_ok, msg = validate("  valid_user_1  ", "Пароль123!", "Пароль123!")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")

    def test_complex_valid_password(self):
        """Сложный валидный пароль с разными спецсимволами"""
        is_ok, msg = validate("user_test_123", "П@роль_123?", "П@роль_123?")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")

    def test_email_with_subdomain(self):
        """Email с поддоменом должен приниматься"""
        is_ok, msg = validate("user@mail.example.com", "Пароль123!", "Пароль123!")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "")


if __name__ == '__main__':
    unittest.main(verbosity=2)
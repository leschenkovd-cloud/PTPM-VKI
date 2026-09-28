import logging
import sys
import re
import hashlib
import os

#директория логов
os.makedirs("logs", exist_ok=True)
# Шаблон строки лога (аналог template в Serilog)
# Содержит: время, уровень (до 7 символов для выравнивания), имя логгера и сообщение
log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Базовая настройка корневого логгера
logging.basicConfig(
    level=logging.DEBUG, # Минимальный уровень логирования (аналог MinimumLevel.Debug)
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),          # Настройка логирования в консоль
        logging.FileHandler("logs/file_txt.log", encoding="utf-8") # Настройка логирования в файл
    ]
)

logger = logging.getLogger(__name__)
logging.info("Логгер успешно сконфигурирован")
logging.info("Приложение запущено")

BLACKLIST = {"admin", "root", "user", "test", "administrator", "support"}

# Маска телефона
PHONE_PATTERN = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
# Маска email
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
# Строковый логин
STRING_LOGIN_PATTERN = re.compile(r"^[a-zA-Z0-9_]{5,}$")

# Спецсимволы
SPECIAL_CHARS = r'!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?'
#ТОЛЬКО кириллица, цифры и спецсимволы
PASSWORD_ALLOWED_CHARS_PATTERN = re.compile(rf"^[а-яА-ЯёЁ0-9{re.escape(SPECIAL_CHARS)}]+$")

def mask_password(pwd: str) -> str:
    """
    Безопасное маскирование пароля для логирования.
    Использует хеш SHA-256, что гарантирует:
    - Одинаковый результат для одинаковых паролей.
    - Разный результат для разных паролей.
    - Невозможность восстановления исходного пароля из лога.
    """
    if not pwd:
        return "***EMPTY***"
    pwd_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()[:12]
    return f"***MASKED_HASH:{pwd_hash}***"


def validate_registration(login: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Осуществляет комплексную валидацию учетных данных при регистрации.
    Возвращает кортеж: (Результат (bool), Сообщение (str)).
    """
    # Приводим к строке и убираем крайние пробелы для логина (но не для пароля!)
    login = str(login).strip() if login else ""
    password = str(password) if password else ""
    confirm_password = str(confirm_password) if confirm_password else ""

    try:
        # --- ВАЛИДАЦИЯ ЛОГИНА ---
        if not login:
            return False, "Ошибка: Логин не может быть пустым."

        is_phone = bool(PHONE_PATTERN.match(login))
        is_email = bool(EMAIL_PATTERN.match(login))
        is_string = bool(STRING_LOGIN_PATTERN.match(login))

        if not (is_phone or is_email or is_string):
            # Детализация ошибки для строкового логина, если он был близок к истине
            if len(login) < 5 and re.match(r"^[a-zA-Z0-9_]+$", login):
                return False, "Ошибка: Строковый логин должен содержать минимум 5 символов."
            if not re.match(r"^[a-zA-Z0-9_@.+-]+$", login) and not PHONE_PATTERN.match(login.replace(" ", "")):
                return False, "Ошибка: Логин содержит недопустимые символы. Разрешены: латиница, цифры, _, @, ., +, -."

            return False, "Ошибка: Неверный формат логина. Допустимы: телефон (+x-xxx-xxx-xxxx), корректный email или строка (мин. 5 символов, латиница, цифры, _)."

        if login.lower() in BLACKLIST:
            return False, f"Ошибка: Логин '{login}' находится в черном списке и не может быть использован."

        # --- ВАЛИДАЦИЯ ПАРОЛЯ ---
        if not password:
            return False, "Ошибка: Пароль не может быть пустым."

        if len(password) < 7:
            return False, "Ошибка: Пароль должен содержать минимум 7 символов."

        if not re.search(r'[А-ЯЁ]', password):
            return False, "Ошибка: Пароль должен содержать минимум одну заглавную букву кириллицы."

        if not re.search(r'[а-яё]', password):
            return False, "Ошибка: Пароль должен содержать минимум одну строчную букву кириллицы."

        if not re.search(r'\d', password):
            return False, "Ошибка: Пароль должен содержать минимум одну цифру."

        if not re.search(f'[{re.escape(SPECIAL_CHARS)}]', password):
            return False, f"Ошибка: Пароль должен содержать минимум один спецсимвол ({SPECIAL_CHARS})."

        if not PASSWORD_ALLOWED_CHARS_PATTERN.match(password):
            return False, "Ошибка: Пароль может содержать ТОЛЬКО кириллицу, цифры и спецсимволы (латиница запрещена)."

        # --- ПРОВЕРКА СОВПАДЕНИЯ ---
        if password != confirm_password:
            return False, "Ошибка: Пароль и подтверждение пароля не совпадают."

        # --- УСПЕХ ---
        return True, ""

    except Exception as e:
        # Логирование непредвиденных ошибок с трассировкой стека
        error_msg = f"Критический сбой при валидации: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, "Ошибка: Внутренняя ошибка сервера при проверке данных."


# ==============================================================================
# 5. ДЕМО-ТЕСТИРОВАНИЕ И ЛОГИРОВАНИЕ РЕЗУЛЬТАТОВ
# ==============================================================================

def process_registration_attempt(login: str, password: str, confirm_password: str):
    """Обертка для демонстрации сквозного логирования."""
    logger.info(
        f"Получен запрос на регистрацию. Логин: '{login}', Пароль: {mask_password(password)}, Подтверждение: {mask_password(confirm_password)}")

    is_valid, message = validate_registration(login, password, confirm_password)

    if is_valid:
        logger.info(f"Успешная валидация. Логин: '{login}', Результат: True. Регистрация разрешена.")
    else:
        logger.warning(f"Неуспешная валидация. Логин: '{login}', Результат: False. Причина: {message}")

    return is_valid, message


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" ЗАПУСК ТЕСТОВ ВАЛИДАЦИИ (Вариант 2) ".center(80, "="))
    print("=" * 80 + "\n")

    # Тест 1: Успешная регистрация (Кириллица, цифры, спецсимволы)
    process_registration_attempt("user_valid_123", "Пароль123!", "Пароль123!")

    # Тест 2: Успешная регистрация (Телефон)
    process_registration_attempt("+7-999-123-4567", "Секретный_Пароль2026#", "Секретный_Пароль2026#")

    # Тест 3: Ошибка - логин в черном списке
    process_registration_attempt("admin", "Пароль123!", "Пароль123!")

    # Тест 4: Ошибка - короткий строковый логин
    process_registration_attempt("usr", "Пароль123!", "Пароль123!")

    # Тест 5: Ошибка - пароль содержит латиницу (запрещено по условию)
    process_registration_attempt("valid_login_99", "Password123!", "Password123!")

    # Тест 6: Ошибка - нет заглавной кириллической буквы
    process_registration_attempt("valid_login_99", "пароль123!", "пароль123!")

    # Тест 7: Ошибка - нет спецсимвола
    process_registration_attempt("valid_login_99", "Пароль123", "Пароль123")

    # Тест 8: Ошибка - несовпадение паролей (демонстрация разного маскирования)
    process_registration_attempt("valid_login_99", "Пароль123!", "ДругойПароль456!")

    # Тест 9: Ошибка - неверный формат телефона
    process_registration_attempt("+79991234567", "Пароль123!", "Пароль123!")

    # Тест 10: Ошибка - пустой пароль
    process_registration_attempt("valid_login_99", "", "Пароль123!")

    print("\n" + "=" * 80)
    print(" ТЕСТЫ ЗАВЕРШЕНЫ. Проверьте файл logs/file_txt.log ".center(80, "="))
    print("=" * 80 + "\n")

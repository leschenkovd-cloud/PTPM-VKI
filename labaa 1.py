import logging, sys, re, hashlib, os

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | [%(levelname)-7s] | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("logs/file_txt.log", encoding="utf-8")]
)
logger = logging.getLogger(__name__)


# Маскирование (детерминированное: одинаковый пароль = одинаковый хеш
def mask(p): return f"***{hashlib.sha256(p.encode()).hexdigest()[:8]}***" if p else "***EMPTY***"


# Основная валидация (возвращает >10 уникальных ошибок)
def validate(login, pwd, pwd2):
    login = str(login).strip()

    # Проверки логина
    if not login: return False, "Логин пуст"
    is_phone = bool(re.match(r"^\+\d-\d{3}-\d{3}-\d{4}$", login))
    is_email = bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", login))
    is_str = bool(re.match(r"^[a-zA-Z0-9_]{5,}$", login))
    if not (is_phone or is_email or is_str): return False, "Неверный формат логина"
    if login.lower() in {"admin", "root", "user", "test"}: return False, "Логин в черном списке"

    # Проверки пароля
    if not pwd: return False, "Пароль пуст"
    if len(pwd) < 7: return False, "Пароль короче 7 символов"
    # Только кириллица, цифры и спецсимволы (латиница запрещена)
    if not re.match(r"^[а-яА-ЯёЁ0-9!@#$%^&*()_+?=\-]+$",
                    pwd): return False, "Пароль содержит недопустимые символы (например, латиницу)"
    if not re.search(r"[А-ЯЁ]", pwd): return False, "Нет заглавной кириллицы"
    if not re.search(r"[а-яё]", pwd): return False, "Нет строчной кириллицы"
    if not re.search(r"\d", pwd): return False, "Нет цифры"
    if not re.search(r"[!@#$%^&*()_+?=\-]", pwd): return False, "Нет спецсимвола"

    # Совпадение
    if pwd != pwd2: return False, "Пароли не совпадают"

    return True, ""

# Обертка для логирования запроса
def process(login, pwd, pwd2):
    logger.info(f"Запрос: логин='{login}', пароль={mask(pwd)}")
    is_ok, msg = validate(login, pwd, pwd2)
    if is_ok:
        logger.info(f"Успех: регистрация '{login}' разрешена.")
    else:
        logger.warning(f"Отказ: '{login}'. Причина: {msg}")
    return is_ok, msg


# Демонстрация (можно быстро удалить или закомментировать)
if __name__ == "__main__":
    process("valid_user_1", "Пароль123!", "Пароль123!")  # Успех
    process("admin", "Пароль123!", "Пароль123!")  # Ошибка: черный список
    process("user_1", "password123!", "password123!")  # Ошибка: нет заглавной кириллицы
    process("user_1", "Пароль123!", "Пароль124!")  # Ошибка: не совпадают (хэши в логе будут разные)
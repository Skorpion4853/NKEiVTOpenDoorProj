import logging


def write_warning(name, message):
    # Создаем логгер
    logger = logging.getLogger(name)

    # Создаем обработчик для записи в файл
    file_handler = logging.FileHandler('logs/app.log', mode='a', encoding='utf-8')  # 'w' - перезаписать, 'a' - дописать
    file_handler.setLevel(logging.DEBUG)

    # Создаем форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Добавляем форматтер к обработчику
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)
    logger.warning(message)


def write_error(name, message):
    # Создаем логгер
    logger = logging.getLogger(name)

    # Создаем обработчик для записи в файл
    file_handler = logging.FileHandler('logs/app.log', mode='a', encoding='utf-8')  # 'w' - перезаписать, 'a' - дописать
    file_handler.setLevel(logging.DEBUG)

    # Создаем форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Добавляем форматтер к обработчику
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)
    logger.error(message)



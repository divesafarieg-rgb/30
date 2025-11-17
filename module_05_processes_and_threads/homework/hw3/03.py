class BlockErrors:

    def __init__(self, error_types):
        if isinstance(error_types, type) and issubclass(error_types, BaseException):
            self.error_types = (error_types,)
        else:
            self.error_types = tuple(error_types)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            if issubclass(exc_type, self.error_types):
                return True
        return False


if __name__ == "__main__":
    print("Демонстрация работы BlockErrors:")

    print("Пример 1:")
    err_types = {ZeroDivisionError, TypeError}
    with BlockErrors(err_types):
        a = 1 / 0
    print('Выполнено без ошибок')

    print("\nПример с одним исключением:")
    with BlockErrors(ZeroDivisionError):
        a = 1 / 0
    print('Выполнено без ошибок (одиночное исключение)')

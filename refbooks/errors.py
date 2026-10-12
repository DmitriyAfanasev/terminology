class NotFoundError(Exception):
    """Запрошенный объект не найден."""


class RefbookNotFound(NotFoundError):
    def __init__(self, refbook_id: int) -> None:
        super().__init__(f"Справочник с id={refbook_id} не найден.")


class VersionNotFound(NotFoundError):
    def __init__(self, refbook_id: int, version: str | None) -> None:
        if version is None:
            msg = f"У справочника id={refbook_id} нет текущей версии."
        else:
            msg = f"У справочника id={refbook_id} нет версии «{version}»."
        super().__init__(msg)

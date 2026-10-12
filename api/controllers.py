from http import HTTPStatus

from dmr import APIError, Controller, Path, Query
from dmr.errors import ErrorType
from dmr.plugins.pydantic import PydanticSerializer

from refbooks import errors, services

from . import schemas


class RefbookListController(Controller[PydanticSerializer]):
    async def get(self, parsed_query: Query[schemas.RefbookListQuery]) -> schemas.RefbookListOut:
        """
        Список справочников.

        Если указан параметр `date`, то возвращаются только справочники, в которых есть
        версия с датой начала действия раньше или равной указанной.
        """
        refbooks = await services.list_refbooks(parsed_query.date)
        return schemas.RefbookListOut(
            refbooks=[
                schemas.RefbookOut(id=str(r.pk), code=r.code, name=r.name)
                for r in refbooks
            ]
        )


class ElementListController(Controller[PydanticSerializer]):
    async def get(
        self,
        parsed_path: Path[schemas.RefbookPath],
        parsed_query: Query[schemas.ElementsQuery],
    ) -> schemas.ElementListOut:
        """
        Элементы справочника.

        Если версия не указана — элементы текущей версии: той, дата начала действия которой
        позже всех остальных, но не позже сегодняшней даты.
        """
        try:
            elements = await services.list_elements(parsed_path.refbook_id, parsed_query.version)
        except errors.NotFoundError as exc:
            raise APIError(self.format_error(str(exc), error_type=ErrorType.user_msg), status_code=HTTPStatus.NOT_FOUND)
        return schemas.ElementListOut(
            elements=[
                schemas.ElementOut(code=element.code, value=element.value)
                for element in elements
            ]
        )


class CheckElementController(Controller[PydanticSerializer]):
    async def get(
        self,
        parsed_path: Path[schemas.RefbookPath],
        parsed_query: Query[schemas.CheckElementQuery],
    ) -> schemas.CheckElementOut:
        """
        Валидация элемента справочника.

        Проверяет, что элемент с данными кодом и значением присутствует в указанной версии
        справочника. Если версия не указана — проверяется текущая версия.
        """
        try:
            valid = await services.check_element(
                parsed_path.refbook_id,
                parsed_query.code,
                parsed_query.value,
                parsed_query.version,
            )
        except errors.NotFoundError as exc:
            raise APIError(self.format_error(str(exc), error_type=ErrorType.user_msg), status_code=HTTPStatus.NOT_FOUND)
        return schemas.CheckElementOut(valid=valid)

import datetime as dt

from pydantic import BaseModel, Field


class RefbookListQuery(BaseModel):
    date: dt.date | None = Field(
        default=None,
        description="Дата в формате ГГГГ-ММ-ДД. Вернутся только справочники, у которых есть "
        "версия с датой начала действия раньше или равной указанной.",
        examples=["2026-10-12"],
    )


class RefbookPath(BaseModel):
    refbook_id: int = Field(description="Идентификатор справочника.")


class ElementsQuery(BaseModel):
    version: str | None = Field(
        default=None,
        max_length=50,
        description="Версия справочника. Если не указана — используется текущая версия.",
        examples=["1.0"],
    )


class CheckElementQuery(BaseModel):
    code: str = Field(max_length=100, description="Код элемента справочника.")
    value: str = Field(max_length=300, description="Значение элемента справочника.")
    version: str | None = Field(
        default=None,
        max_length=50,
        description="Версия справочника. Если не указана — используется текущая версия.",
    )


class RefbookOut(BaseModel):
    id: str = Field(description="Идентификатор справочника.", examples=["1"])
    code: str = Field(description="Код справочника.", examples=["MS1"])
    name: str = Field(
        description="Наименование справочника.",
        examples=["Специальности медицинских работников"],
    )


class RefbookListOut(BaseModel):
    refbooks: list[RefbookOut]


class ElementOut(BaseModel):
    code: str = Field(description="Код элемента.", examples=["J00"])
    value: str = Field(
        description="Значение элемента.", examples=["Острый назофарингит (насморк)"]
    )


class ElementListOut(BaseModel):
    elements: list[ElementOut]


class CheckElementOut(BaseModel):
    valid: bool = Field(
        description="true — элемент с таким кодом и значением есть в указанной версии справочника."
    )

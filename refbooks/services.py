import datetime as dt
from dataclasses import dataclass

from django.utils import timezone

from refbooks.errors import RefbookNotFound, VersionNotFound
from refbooks.models import Refbook, RefbookElement, RefbookVersion


@dataclass(frozen=True, slots=True)
class ElementData:
    code: str
    value: str


def list_refbooks(on_date: dt.date | None = None) -> list[Refbook]:
    """Список справочников.

    Если задана дата — только справочники, у которых есть версия с датой начала
    действия, раньше или равной указанной.
    """
    qs = Refbook.objects.order_by("id")
    if on_date is not None:
        qs = qs.filter(versions__start_date__lte=on_date).distinct()
    return list(qs)


def get_refbook(refbook_id: int) -> Refbook:
    try:
        return Refbook.objects.get(pk=refbook_id)
    except Refbook.DoesNotExist:
        raise RefbookNotFound(refbook_id)


def resolve_version(refbook_id: int, version: str | None) -> RefbookVersion:
    """Находит версию справочника.

    Без параметра ``version`` возвращает текущую версию: с самой поздней датой
    начала действия, но не позже сегодняшнего дня.
    """
    get_refbook(refbook_id)
    qs = RefbookVersion.objects.filter(refbook_id=refbook_id)
    if version is None:
        found = qs.filter(start_date__lte=timezone.localdate()).order_by("-start_date").first()
    else:
        found = qs.filter(version=version).first()
    if found is None:
        raise VersionNotFound(refbook_id, version)
    return found


def list_elements(refbook_id: int, version: str | None = None) -> list[ElementData]:
    resolved = resolve_version(refbook_id, version)
    qs = RefbookElement.objects.filter(version=resolved).order_by("id")
    return [ElementData(code=e.code, value=e.value) for e in qs]


def check_element(refbook_id: int, code: str, value: str, version: str | None = None) -> bool:
    """Есть ли в версии справочника элемент с данными кодом и значением."""
    resolved = resolve_version(refbook_id, version)
    return RefbookElement.objects.filter(version=resolved, code=code, value=value).exists()

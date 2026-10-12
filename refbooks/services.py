import datetime as dt
from dataclasses import dataclass

from django.utils import timezone

from .errors import RefbookNotFound, VersionNotFound
from .models import Refbook, RefbookElement, RefbookVersion


async def list_refbooks(on_date: dt.date | None = None) -> list[Refbook]:
    """Список справочников.

    Если задана дата — только справочники, у которых есть версия с датой начала
    действия, раньше или равной указанной.
    """
    qs = Refbook.objects.order_by("id")
    if on_date is not None:
        qs = qs.filter(versions__start_date__lte=on_date).distinct()
    return [refbook async for refbook in qs]


async def get_refbook(refbook_id: int) -> Refbook:
    try:
        return await Refbook.objects.aget(pk=refbook_id)
    except Refbook.DoesNotExist:
        raise RefbookNotFound(refbook_id) from None


async def resolve_version(refbook_id: int, version: str | None) -> RefbookVersion:
    """Находит версию справочника.

    Без параметра ``version`` возвращает текущую версию: с самой поздней датой
    начала действия, но не позже сегодняшнего дня.
    """
    await get_refbook(refbook_id)
    qs = RefbookVersion.objects.filter(refbook_id=refbook_id)
    if version is None:
        found = await qs.filter(start_date__lte=timezone.localdate()).order_by("-start_date").afirst()
    else:
        found = await qs.filter(version=version).afirst()
    if found is None:
        raise VersionNotFound(refbook_id, version)
    return found


async def list_elements(refbook_id: int, version: str | None = None) -> list[ElementData]:
    resolved = await resolve_version(refbook_id, version)
    qs = RefbookElement.objects.filter(version=resolved).order_by("id")
    return [ElementData(code=e.code, value=e.value) async for e in qs]


async def check_element(refbook_id: int, code: str, value: str, version: str | None = None) -> bool:
    """Есть ли в версии справочника элемент с данными кодом и значением."""
    resolved = await resolve_version(refbook_id, version)
    return await RefbookElement.objects.filter(version=resolved, code=code, value=value).aexists()


@dataclass(frozen=True, slots=True)
class ElementData:
    code: str
    value: str

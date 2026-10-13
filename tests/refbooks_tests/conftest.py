import datetime as dt
from dataclasses import dataclass

import pytest
from django.utils import timezone

from refbooks.models import Refbook, RefbookElement, RefbookVersion


@dataclass(frozen=True, slots=True)
class SeedData:
    ms: Refbook
    icd: Refbook
    v1: RefbookVersion
    v2: RefbookVersion
    v3: RefbookVersion
    icd_v: RefbookVersion


@pytest.fixture
def api_prefix() -> str:
    return "/api"


@pytest.fixture
def today() -> dt.date:
    return timezone.localdate()


@pytest.fixture
def data(db, today: dt.date) -> SeedData:
    """
    Справочник «MS1» с тремя версиями:
      * 1.0 — начала действовать давно (прошлая версия);
      * 2.0 — действует сейчас (текущая);
      * 3.0 — начнёт действовать в будущем.
    Справочник «ICD-10» с единственной версией, которая начнётся в будущем.
    """
    ms = Refbook.objects.create(code="MS1", name="Специальности медицинских работников")
    icd = Refbook.objects.create(code="ICD-10", name="МКБ-10", description="Диагнозы")

    v1 = RefbookVersion.objects.create(
        refbook=ms, version="1.0", start_date=today - dt.timedelta(days=400)
    )
    v2 = RefbookVersion.objects.create(
        refbook=ms, version="2.0", start_date=today - dt.timedelta(days=10)
    )
    v3 = RefbookVersion.objects.create(
        refbook=ms, version="3.0", start_date=today + dt.timedelta(days=30)
    )
    icd_v = RefbookVersion.objects.create(
        refbook=icd, version="1", start_date=today + dt.timedelta(days=5)
    )

    for code, value in [("1", "Врач-терапевт"), ("2", "Травматолог-ортопед"), ("3", "Хирург")]:
        RefbookElement.objects.create(version=v1, code=code, value=value)

    for code, value in [("1", "Терапевт"), ("2", "Травматолог"), ("4", "Окулист")]:
        RefbookElement.objects.create(version=v2, code=code, value=value)

    RefbookElement.objects.create(version=v3, code="9", value="Будущий элемент")
    RefbookElement.objects.create(
        version=icd_v,
        code="S99",
        value="Другие и неуточненные травмы голеностопного сустава и стопы",
    )

    return SeedData(ms=ms, icd=icd, v1=v1, v2=v2, v3=v3, icd_v=icd_v)

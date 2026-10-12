import datetime as dt

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from refbooks.models import Refbook, RefbookElement, RefbookVersion

pytestmark = pytest.mark.django_db


def test_refbook_code_is_unique():
    Refbook.objects.create(code="A", name="a")
    with pytest.raises(IntegrityError), transaction.atomic():
        Refbook.objects.create(code="A", name="other")


def test_version_unique_per_refbook():
    rb = Refbook.objects.create(code="A", name="a")
    RefbookVersion.objects.create(refbook=rb, version="1", start_date=dt.date(2022, 1, 1))
    with pytest.raises(IntegrityError), transaction.atomic():
        RefbookVersion.objects.create(refbook=rb, version="1", start_date=dt.date(2023, 1, 1))


def test_version_start_date_unique_per_refbook():
    rb = Refbook.objects.create(code="A", name="a")
    RefbookVersion.objects.create(refbook=rb, version="1", start_date=dt.date(2022, 1, 1))
    with pytest.raises(IntegrityError), transaction.atomic():
        RefbookVersion.objects.create(refbook=rb, version="2", start_date=dt.date(2022, 1, 1))


def test_same_version_and_date_allowed_in_different_refbooks():
    a = Refbook.objects.create(code="A", name="a")
    b = Refbook.objects.create(code="B", name="b")
    RefbookVersion.objects.create(refbook=a, version="1", start_date=dt.date(2022, 1, 1))
    RefbookVersion.objects.create(refbook=b, version="1", start_date=dt.date(2022, 1, 1))


def test_element_code_unique_per_version():
    rb = Refbook.objects.create(code="A", name="a")
    v1 = RefbookVersion.objects.create(refbook=rb, version="1", start_date=dt.date(2022, 1, 1))
    v2 = RefbookVersion.objects.create(refbook=rb, version="2", start_date=dt.date(2023, 1, 1))
    RefbookElement.objects.create(version=v1, code="x", value="1")
    with pytest.raises(IntegrityError), transaction.atomic():
        RefbookElement.objects.create(version=v1, code="x", value="2")
    RefbookElement.objects.create(version=v2, code="x", value="1")  # в другой версии можно


def test_constraints_give_russian_validation_messages():
    rb = Refbook.objects.create(code="A", name="a")
    RefbookVersion.objects.create(refbook=rb, version="1", start_date=dt.date(2022, 1, 1))
    dup = RefbookVersion(refbook=rb, version="1", start_date=dt.date(2024, 1, 1))
    with pytest.raises(ValidationError) as exc:
        dup.full_clean()
    assert "уже есть версия" in str(exc.value)


def test_version_str_is_refbook_dash_version():
    rb = Refbook.objects.create(code="MS1", name="a")
    assert (
        str(RefbookVersion(refbook=rb, version="1.0", start_date=dt.date(2022, 1, 1))) == "MS1-1.0"
    )

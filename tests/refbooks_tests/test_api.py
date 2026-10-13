import datetime as dt
from http import HTTPStatus
from urllib.parse import urlencode

import pytest
from django.test import Client

from .conftest import SeedData


def test_list_refbooks_without_date(client: Client, api_prefix: str, data: SeedData) -> None:
    response = client.get(f"{api_prefix}/refbooks/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "refbooks": [
            {
                "id": str(data.ms.pk),
                "code": "MS1",
                "name": "Специальности медицинских работников",
            },
            {"id": str(data.icd.pk), "code": "ICD-10", "name": "МКБ-10"},
        ]
    }


def test_list_refbooks_with_date_filters_by_version_start(
    client: Client,
    api_prefix: str,
    data: SeedData,
    today: dt.date
) -> None:
    """Сегодня уже действует только MS1; у ICD-10 версия начнётся через 5 дней."""
    response = client.get(f"{api_prefix}/refbooks/?date={today.isoformat()}")
    assert [r["code"] for r in response.json()["refbooks"]] == ["MS1"]

    in_a_week = today + dt.timedelta(days=7)
    response = client.get(f"{api_prefix}/refbooks/?date={in_a_week.isoformat()}")
    assert [r["code"] for r in response.json()["refbooks"]] == ["MS1", "ICD-10"]


def test_list_refbooks_date_equal_to_start_date_is_included(
    client: Client,
    api_prefix: str,
    data: SeedData,
) -> None:
    start = data.icd_v.start_date

    response = client.get(f"{api_prefix}/refbooks/?date={start.isoformat()}")

    assert "ICD-10" in [r["code"] for r in response.json()["refbooks"]]


def test_list_refbooks_date_before_any_version_returns_empty(
    client: Client,
    api_prefix: str,
    data: SeedData
) -> None:
    response = client.get(f"{api_prefix}/refbooks/?date=1999-01-01")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"refbooks": []}


def test_list_refbooks_no_duplicates_for_multiple_versions(
    client: Client,
    api_prefix: str,
    data: SeedData
) -> None:
    """У MS1 две версии подходят под дату — справочник должен вернуться один раз."""
    response = client.get(f"{api_prefix}/refbooks/?date=2999-01-01")

    assert [r["code"] for r in response.json()["refbooks"]].count("MS1") == 1


def test_list_refbooks_invalid_date_is_bad_request(
    client: Client,
    api_prefix: str,
    data: SeedData
) -> None:
    response = client.get(f"{api_prefix}/refbooks/?date=not-a-date")

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_elements_default_is_current_version(
    client: Client, api_prefix: str, data: SeedData
) -> None:
    response = client.get(f"{api_prefix}/refbooks/{data.ms.pk}/elements")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "elements": [
            {"code": "1", "value": "Терапевт"},
            {"code": "2", "value": "Травматолог"},
            {"code": "4", "value": "Окулист"},
        ]
    }


def test_elements_explicit_version(client: Client, api_prefix: str, data: SeedData) -> None:
    response = client.get(f"{api_prefix}/refbooks/{data.ms.pk}/elements?version=1.0")

    assert [e["value"] for e in response.json()["elements"]] == [
        "Врач-терапевт",
        "Травматолог-ортопед",
        "Хирург",
    ]


def test_elements_future_version_can_be_requested_explicitly(
    client: Client,
    api_prefix: str,
    data: SeedData,
) -> None:
    response = client.get(f"{api_prefix}/refbooks/{data.ms.pk}/elements?version=3.0")

    assert response.json() == {"elements": [{"code": "9", "value": "Будущий элемент"}]}


def test_elements_unknown_refbook_is_not_found(
    client: Client,
    api_prefix: str,
    data: SeedData,
) -> None:
    response = client.get(f"{api_prefix}/refbooks/9999/elements")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_elements_unknown_version_is_not_found(
    client: Client,
    api_prefix: str,
    data: SeedData,
) -> None:
    response = client.get(f"{api_prefix}/refbooks/{data.ms.pk}/elements?version=7.7")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_elements_no_current_version_is_not_found(
    client: Client, api_prefix: str, data: SeedData
) -> None:
    """У ICD-10 единственная версия начнётся в будущем — текущей версии нет."""
    response = client.get(f"{api_prefix}/refbooks/{data.icd.pk}/elements")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_elements_version_is_scoped_to_refbook(
    client: Client, api_prefix: str, data: SeedData
) -> None:
    """Версия «1» принадлежит ICD-10, у MS1 такой версии нет."""
    foreign = client.get(f"{api_prefix}/refbooks/{data.ms.pk}/elements?version=1")
    own = client.get(f"{api_prefix}/refbooks/{data.icd.pk}/elements?version=1")

    assert foreign.status_code == HTTPStatus.NOT_FOUND
    assert own.status_code == HTTPStatus.OK

def check_url(prefix: str, refbook_id: int, **params: str) -> str:
    return f"{prefix}/refbooks/{refbook_id}/check_element?{urlencode(params)}"


def test_check_element_found_in_current_version(
    client: Client, api_prefix: str, data: SeedData
) -> None:
    response = client.get(check_url(api_prefix, data.ms.pk, code="1", value="Терапевт"))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"valid": True}


def test_check_element_wrong_value(client: Client, api_prefix: str, data: SeedData) -> None:
    response = client.get(check_url(api_prefix, data.ms.pk, code="1", value="Хирург"))

    assert response.json() == {"valid": False}


def test_check_element_depends_on_version(client: Client, api_prefix: str, data: SeedData) -> None:
    # «Хирург» есть только в версии 1.0.
    current = client.get(check_url(api_prefix, data.ms.pk, code="3", value="Хирург"))
    old = client.get(check_url(api_prefix, data.ms.pk, code="3", value="Хирург", version="1.0"))

    assert current.json() == {"valid": False}
    assert old.json() == {"valid": True}


@pytest.mark.parametrize("query", ["", "?code=1", "?value=x"])
def test_check_element_missing_params_is_bad_request(
    client: Client,
    api_prefix: str,
    data: SeedData,
    query: str
) -> None:
    response = client.get(f"{api_prefix}/refbooks/{data.ms.pk}/check_element{query}")

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_check_element_unknown_refbook_is_not_found(
    client: Client,
    api_prefix: str,
    data: SeedData
) -> None:
    response = client.get(check_url(api_prefix, 9999, code="1", value="x"))

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_check_element_unknown_version_is_not_found(
    client: Client,
    api_prefix: str,
    data: SeedData
) -> None:
    url = check_url(api_prefix, data.ms.pk, code="1", value="Терапевт", version="42")

    response = client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

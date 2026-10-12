import datetime as dt

from django.core.management.base import BaseCommand
from django.db import transaction

from refbooks.models import Refbook, RefbookElement, RefbookVersion

DEMO = [
    {
        "code": "MS1",
        "name": "Специальности медицинских работников",
        "description": "Справочник специальностей медицинских работников.",
        "versions": [
            (
                "1.0",
                dt.date(2022, 1, 1),
                [("1", "Врач-терапевт"), ("2", "Травматолог-ортопед"), ("3", "Хирург")],
            ),
            (
                "2.0",
                dt.date(2023, 1, 1),
                [
                    ("1", "Врач-терапевт"),
                    ("2", "Травматолог-ортопед"),
                    ("3", "Хирург"),
                    ("4", "Офтальмолог"),
                ],
            ),
        ],
    },
    {
        "code": "ICD-10",
        "name": "МКБ-10",
        "description": "Международная классификация болезней 10-го пересмотра.",
        "versions": [
            (
                "1.0",
                dt.date(2022, 1, 1),
                [
                    ("J00", "Острый назофарингит (насморк)"),
                    ("J01", "Острый синусит"),
                    ("S99", "Другие и неуточненные травмы голеностопного сустава и стопы"),
                ],
            ),
        ],
    },
]


class Command(BaseCommand):
    help = "Создаёт демонстрационные справочники."

    @transaction.atomic
    def handle(self, *args, **options):
        for item in DEMO:
            refbook, _ = Refbook.objects.get_or_create(
                code=item["code"],
                defaults={"name": item["name"], "description": item["description"]},
            )
            for version, start, elements in item["versions"]:
                ver, _ = RefbookVersion.objects.get_or_create(
                    refbook=refbook, version=version, defaults={"start_date": start}
                )
                for code, value in elements:
                    RefbookElement.objects.get_or_create(
                        version=ver, code=code, defaults={"value": value}
                    )
        self.stdout.write(self.style.SUCCESS("Демо-данные созданы."))

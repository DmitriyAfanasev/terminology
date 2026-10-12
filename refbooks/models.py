from django.db import models


class Refbook(models.Model):
    """Справочник."""

    code = models.CharField("Код", max_length=100, unique=True)
    name = models.CharField("Наименование", max_length=300)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "справочник"
        verbose_name_plural = "справочники"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def __repr__(self) -> str:
        return str(self)


class RefbookVersion(models.Model):
    """Версия справочника."""

    refbook = models.ForeignKey(
        Refbook,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name="Справочник",
    )
    version = models.CharField("Версия", max_length=50)
    start_date = models.DateField("Дата начала действия версии")

    class Meta:
        verbose_name = "версия справочника"
        verbose_name_plural = "версии справочников"
        ordering = ["refbook_id", "-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["refbook", "version"],
                name="uniq_refbook_version",
                violation_error_message="У справочника уже есть версия с таким номером.",
            ),
            models.UniqueConstraint(
                fields=["refbook", "start_date"],
                name="uniq_refbook_start_date",
                violation_error_message=(
                    "У справочника уже есть версия с такой датой начала действия."
                ),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.refbook.code}-{self.version}"

    def __repr__(self) -> str:
        return str(self)


class RefbookElement(models.Model):
    """Элемент справочника."""

    version = models.ForeignKey(
        RefbookVersion,
        on_delete=models.CASCADE,
        related_name="elements",
        verbose_name="Версия",
    )
    code = models.CharField("Код элемента", max_length=100)
    value = models.CharField("Значение элемента", max_length=300)

    class Meta:
        verbose_name = "элемент справочника"
        verbose_name_plural = "элементы справочников"
        ordering = ["version_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["version", "code"],
                name="uniq_version_element_code",
                violation_error_message="В этой версии уже есть элемент с таким кодом.",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.value}"

    def __repr__(self) -> str:
        return str(self)

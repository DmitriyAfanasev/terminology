from django.contrib import admin
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from .models import Refbook, RefbookElement, RefbookVersion

admin.site.site_header = "Сервис терминологии"
admin.site.site_title = "Сервис терминологии"
admin.site.index_title = "Управление справочниками"


class RefbookVersionInline(admin.TabularInline):
    """Версии справочника на странице редактирования справочника."""

    model = RefbookVersion
    extra = 0
    fields = ("version", "start_date")
    show_change_link = True  # переход к редактированию версии и её элементов


class RefbookElementInline(admin.TabularInline):
    """Элементы справочника на странице редактирования версии."""

    model = RefbookElement
    extra = 1
    fields = ("code", "value")


@admin.register(Refbook)
class RefbookAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "current_version", "current_version_start")
    list_display_links = ("id", "code")
    search_fields = ("code", "name")
    inlines = [RefbookVersionInline]

    def get_queryset(self, request):
        # Текущая версия — с самой поздней датой начала, но не позже сегодня.
        current = RefbookVersion.objects.filter(
            refbook=OuterRef("pk"), start_date__lte=timezone.localdate()
        ).order_by("-start_date")
        return (
            super()
            .get_queryset(request)
            .annotate(
                _current_version=Subquery(current.values("version")[:1]),
                _current_start=Subquery(current.values("start_date")[:1]),
            )
        )

    @admin.display(description="Текущая версия", ordering="_current_version")
    def current_version(self, obj):
        return obj._current_version or "—"

    @admin.display(description="Дата начала действия версии", ordering="_current_start")
    def current_version_start(self, obj):
        return obj._current_start or "—"


@admin.register(RefbookVersion)
class RefbookVersionAdmin(admin.ModelAdmin):
    list_display = ("refbook_code", "refbook_name", "version", "start_date")
    list_filter = ("refbook",)
    search_fields = ("refbook__code", "refbook__name", "version")
    list_select_related = ("refbook",)
    inlines = [RefbookElementInline]

    @admin.display(description="Код справочника", ordering="refbook__code")
    def refbook_code(self, obj):
        return obj.refbook.code

    @admin.display(description="Наименование справочника", ordering="refbook__name")
    def refbook_name(self, obj):
        return obj.refbook.name


@admin.register(RefbookElement)
class RefbookElementAdmin(admin.ModelAdmin):
    list_display = ("version", "code", "value")
    list_filter = ("version__refbook",)
    search_fields = ("code", "value")
    list_select_related = ("version__refbook",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["version"].queryset = RefbookVersion.objects.select_related("refbook")
        return form

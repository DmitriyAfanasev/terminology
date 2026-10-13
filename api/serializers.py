from rest_framework import serializers


class RefbookListQuerySerializer(serializers.Serializer):
    date = serializers.DateField(
        required=False,
        help_text="Дата в формате ГГГГ-ММ-ДД. Вернутся только справочники, у которых есть "
        "версия с датой начала действия раньше или равной указанной.",
    )


class ElementsQuerySerializer(serializers.Serializer):
    version = serializers.CharField(
        required=False,
        max_length=50,
        help_text="Версия справочника. Если не указана — используется текущая версия.",
    )


class CheckElementQuerySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100, help_text="Код элемента справочника.")
    value = serializers.CharField(max_length=300, help_text="Значение элемента справочника.")
    version = serializers.CharField(
        required=False,
        max_length=50,
        help_text="Версия справочника. Если не указана — используется текущая версия.",
    )


class RefbookOutSerializer(serializers.Serializer):
    id = serializers.CharField(source="pk", help_text="Идентификатор справочника.")
    code = serializers.CharField(help_text="Код справочника.")
    name = serializers.CharField(help_text="Наименование справочника.")


class ElementOutSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Код элемента.")
    value = serializers.CharField(help_text="Значение элемента.")


class ElementListOutSerializer(serializers.Serializer):
    elements = ElementOutSerializer(many=True)


class CheckElementOutSerializer(serializers.Serializer):
    valid = serializers.BooleanField(
        help_text="true — элемент с таким кодом и значением есть в указанной версии справочника."
    )


class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()
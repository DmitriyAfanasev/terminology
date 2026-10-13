from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from refbooks import services
from refbooks.errors import NotFoundError
from api.serializers import (
    CheckElementOutSerializer,
    CheckElementQuerySerializer,
    ElementOutSerializer,
    ElementsQuerySerializer,
    ErrorSerializer,
    RefbookListQuerySerializer,
    RefbookOutSerializer,
)

TAG = "Справочники"

ID_PARAM = OpenApiParameter("refbook_id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Идентификатор справочника.")

class RefbookListView(APIView):
    @extend_schema(
        tags=[TAG],
        operation_id="refbooks_list",
        summary="Список справочников",
        description=(
            "Возвращает список справочников. Если указан параметр `date`, то только те "
            "справочники, в которых есть версия с датой начала действия раньше или равной "
            "указанной."
        ),
        parameters=[RefbookListQuerySerializer],
        responses={
            status.HTTP_200_OK: RefbookOutSerializer(many=True),
            status.HTTP_404_NOT_FOUND: ErrorSerializer
        },
        examples=[
            OpenApiExample(
                "Ответ",
                response_only=True,
                status_codes=[str(status.HTTP_200_OK)],
                value={
                    "refbooks": [
                        {"id": "1", "code": "MS1", "name": "Специальности медицинских работников"},
                        {"id": "2", "code": "ICD-10", "name": "МКБ-10"},
                    ]
                },
            ),
        ],
    )
    def get(self, request: Request) -> Response:
        query = RefbookListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        refbooks = services.list_refbooks(query.validated_data.get("date"))
        return Response({"refbooks": RefbookOutSerializer(refbooks, many=True).data})


class ElementListView(APIView):
    @extend_schema(
        tags=[TAG],
        operation_id="refbook_elements",
        summary="Элементы справочника",
        description=(
            "Возвращает элементы заданной версии справочника. Если версия не указана — "
            "элементы текущей версии: той, дата начала действия которой позже всех остальных, "
            "но не позже сегодняшней даты."
        ),
        parameters=[ID_PARAM, ElementsQuerySerializer],
        responses={
            status.HTTP_200_OK: ElementOutSerializer(many=True),
            status.HTTP_400_BAD_REQUEST: ErrorSerializer,
            status.HTTP_404_NOT_FOUND: ErrorSerializer
        },
        examples=[
            OpenApiExample(
                "Ответ",
                response_only=True,
                status_codes=["200"],
                value={
                    "elements": [
                        {"code": "J00", "value": "Острый назофарингит (насморк)"},
                        {"code": "J01", "value": "Острый синусит"},
                    ]
                },
            ),
            OpenApiExample(
                "Справочник не найден",
                response_only=True,
                status_codes=["404"],
                value={"detail": "Справочник с id=99 не найден."},
            ),
        ],
    )
    def get(self, request: Request, refbook_id: int) -> Response:
        query = ElementsQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        try:
            elements = services.list_elements(refbook_id, query.validated_data.get("version"))
        except NotFoundError as exc:
            raise NotFound(str(exc)) from exc
        return Response({"elements": ElementOutSerializer(elements, many=True).data})


class CheckElementView(APIView):
    @extend_schema(
        tags=[TAG],
        operation_id="refbook_check_element",
        summary="Валидация элемента справочника",
        description=(
            "Проверяет, что элемент с данными кодом и значением присутствует в указанной "
            "версии справочника. Если версия не указана — проверяется текущая версия."
        ),
        parameters=[ID_PARAM, CheckElementQuerySerializer],
        responses={
            status.HTTP_200_OK: CheckElementOutSerializer,
            status.HTTP_400_BAD_REQUEST: ErrorSerializer,
            status.HTTP_404_NOT_FOUND: ErrorSerializer
        },
        examples=[
            OpenApiExample(
                "Элемент найден",
                response_only=True,
                status_codes=["200"],
                value={"valid": True},
            ),
            OpenApiExample(
                "Элемент не найден",
                response_only=True,
                status_codes=["200"],
                value={"valid": False},
            ),
        ],
    )
    def get(self, request: Request, refbook_id: int) -> Response:
        query = CheckElementQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        data = query.validated_data
        try:
            valid = services.check_element(
                refbook_id, data["code"], data["value"], data.get("version")
            )
        except NotFoundError as exc:
            raise NotFound(str(exc)) from exc
        return Response({"valid": valid})
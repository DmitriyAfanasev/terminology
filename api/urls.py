from django.urls import path
from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView, RedocView, SwaggerView
from dmr.routing import Router

from . import controllers

router = Router(
    "api/",
    [
        path("refbooks/", controllers.RefbookListController.as_view(), name="refbook-list"),
        path(
            "refbooks/<int:refbook_id>/elements",
            controllers.ElementListController.as_view(),
            name="refbook-elements",
        ),
        path(
            "refbooks/<int:refbook_id>/check_element",
            controllers.CheckElementController.as_view(),
            name="refbook-check-element",
        ),
    ],
    tags=["Справочники"],
)

schema = build_schema(router)

urlpatterns = [
    router.to_urlpatterns(namespace="api"),
    path("openapi.json/", OpenAPIJsonView.as_view(schema=schema), name="dmr-openapi"),
    path("swagger/", SwaggerView.as_view(schema=schema), name="dmr-swagger"),
    path("redoc/", RedocView.as_view(schema=schema), name="dmr-redoc"),
]

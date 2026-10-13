from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from api import views

urlpatterns = [
    path(
        "refbooks/",
        views.RefbookListView.as_view(),
        name="refbook-list",
    ),
    path(
        "refbooks/<int:refbook_id>/elements",
        views.ElementListView.as_view(),
        name="refbook-elements",
    ),
    path(
        "refbooks/<int:refbook_id>/check_element",
        views.CheckElementView.as_view(),
        name="refbook-check-element",
    ),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

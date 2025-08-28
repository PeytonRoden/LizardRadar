from django.urls import path
from .views import radar_map_view, render_radar_image, latest_radar_scan, warnings_json

urlpatterns = [
    path('radar-map/', radar_map_view, name='radar-map'),
    path('api/render-radar/<str:icao>/', render_radar_image, name='render_radar'),
    path("latest-scan/<str:station>/", latest_radar_scan, name="latest_radar_scan"),
    path("api/warnings/", warnings_json, name="warnings_json"),
]

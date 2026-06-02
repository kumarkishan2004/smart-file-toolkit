from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='photo_to_pdf'),
    path('convert/', views.convert, name='photo_to_pdf_convert'),
    path('download/<str:filename>/', views.download, name='photo_to_pdf_download'),
]

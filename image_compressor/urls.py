from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='image_compressor'),
    path('compress/', views.compress, name='image_compressor_compress'),
    path('download/<str:filename>/', views.download, name='image_compressor_download'),
]

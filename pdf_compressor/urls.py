from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='pdf_compressor'),
    path('compress/', views.compress, name='pdf_compressor_compress'),
    path('download/<str:filename>/', views.download, name='pdf_compressor_download'),
]

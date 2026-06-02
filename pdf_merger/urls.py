from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='pdf_merger'),
    path('merge/', views.merge, name='pdf_merger_merge'),
    path('download/<str:filename>/', views.download, name='pdf_merger_download'),
]

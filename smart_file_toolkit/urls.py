"""
URL configuration for Smart File Toolkit.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('photo-to-pdf/', include('photo_to_pdf.urls')),
    path('pdf-merger/', include('pdf_merger.urls')),
    path('pdf-compressor/', include('pdf_compressor.urls')),
    path('image-compressor/', include('image_compressor.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

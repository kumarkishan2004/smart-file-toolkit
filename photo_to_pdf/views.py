"""
Views for Photo to PDF converter.
Converts uploaded images (JPG, PNG, WEBP, etc.) to a single PDF file.
"""
import os
import uuid
import json
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404 ,HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Allowed image types
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/bmp', 'image/tiff']
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per file
MAX_FILES = 20


def index(request):
    """Photo to PDF tool page."""
    return render(request, 'photo_to_pdf/index.html')


@require_POST
def convert(request):
    """Convert uploaded images to a single PDF."""
    try:
        from PIL import Image
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        files = request.FILES.getlist('images')

        # Validate files
        if not files:
            return JsonResponse({'error': 'No images uploaded.'}, status=400)
        if len(files) > MAX_FILES:
            return JsonResponse({'error': f'Maximum {MAX_FILES} images allowed.'}, status=400)

        images = []
        for f in files:
            if f.content_type not in ALLOWED_IMAGE_TYPES:
                return JsonResponse({'error': f'Invalid file type: {f.name}. Only images are allowed.'}, status=400)
            if f.size > MAX_FILE_SIZE:
                return JsonResponse({'error': f'File {f.name} exceeds 20MB limit.'}, status=400)
            try:
                img = Image.open(f)
                img.verify()
                f.seek(0)
                img = Image.open(f)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            except Exception:
                return JsonResponse({'error': f'Could not process image: {f.name}'}, status=400)

        # Create unique output filename
        output_filename = f'converted_{uuid.uuid4().hex}.pdf'
        output_path = Path(settings.TEMP_DIR) / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build PDF using reportlab
        c = canvas.Canvas(str(output_path))

        for img in images:
            width, height = img.size
            # Scale to fit A4 (595 x 842 pts) maintaining aspect ratio
            page_w, page_h = A4
            ratio = min(page_w / width, page_h / height)
            new_w = width * ratio
            new_h = height * ratio
            x = (page_w - new_w) / 2
            y = (page_h - new_h) / 2

            # Save temp image
            tmp_img_path = Path(settings.TEMP_DIR) / f'tmp_{uuid.uuid4().hex}.jpg'
            img.save(str(tmp_img_path), 'JPEG', quality=95)

            c.setPageSize((page_w, page_h))
            c.drawImage(str(tmp_img_path), x, y, new_w, new_h)
            c.showPage()

            # Clean up temp image
            tmp_img_path.unlink(missing_ok=True)

        c.save()

        file_size = output_path.stat().st_size
        return JsonResponse({
            'success': True,
            'filename': output_filename,
            'file_size': _format_size(file_size),
            'pages': len(images),
        })

    except Exception as e:
        return JsonResponse({'error': f'Conversion failed: {str(e)}'}, status=500)




def download(request, filename):
    """Download the file then DELETE it immediately after sending."""
    if '/' in filename or '..' in filename:
        raise Http404

    file_path = Path(settings.TEMP_DIR) / filename
    if not file_path.exists():
        raise Http404('File not found or expired.')

    # Read file into memory FIRST
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # DELETE the file from disk
    try:
        file_path.unlink()
    except Exception:
        pass  # Don't crash if delete fails

    # Send the data from memory (not from disk)
    response = HttpResponse(file_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="SmartFileToolkit_converted.pdf"'
    return response

def _format_size(size_bytes):
    """Format bytes to human readable string."""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.2f} MB'



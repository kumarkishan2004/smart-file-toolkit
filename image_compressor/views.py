"""
Views for Image Compressor.
Compress images with quality control slider.
"""
import uuid
import io
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render

ALLOWED_TYPES = {
    'image/jpeg': ('JPEG', 'jpg'),
    'image/png': ('PNG', 'png'),
    'image/webp': ('WEBP', 'webp'),
    'image/bmp': ('BMP', 'bmp'),
}
MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB


def index(request):
    """Image Compressor tool page."""
    return render(request, 'image_compressor/index.html')


@require_POST
def compress(request):
    """Compress an image with the given quality setting."""
    try:
        from PIL import Image

        f = request.FILES.get('image')
        quality = int(request.POST.get('quality', 75))
        quality = max(5, min(99, quality))

        if not f:
            return JsonResponse({'error': 'No image uploaded.'}, status=400)

        content_type = f.content_type
        # Fallback by extension
        if content_type not in ALLOWED_TYPES:
            ext = f.name.lower().rsplit('.', 1)[-1]
            ext_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                       'webp': 'image/webp', 'bmp': 'image/bmp'}
            content_type = ext_map.get(ext, '')

        if content_type not in ALLOWED_TYPES:
            return JsonResponse({'error': 'Unsupported file type. Use JPG, PNG, WEBP, or BMP.'}, status=400)
        if f.size > MAX_FILE_SIZE:
            return JsonResponse({'error': 'File exceeds 30MB limit.'}, status=400)

        original_size = f.size
        fmt, ext = ALLOWED_TYPES[content_type]

        img = Image.open(f)

        # Convert RGBA to RGB for JPEG
        if fmt == 'JPEG' and img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
            img = background
        elif fmt == 'PNG' and img.mode == 'P':
            img = img.convert('RGBA')

        # Compress to buffer
        buf = io.BytesIO()
        save_kwargs = {'optimize': True}
        if fmt == 'JPEG':
            save_kwargs['quality'] = quality
        elif fmt == 'PNG':
            # PNG quality maps to compression level (0-9)
            compress_level = max(0, min(9, int((100 - quality) / 11)))
            save_kwargs['compress_level'] = compress_level
        elif fmt == 'WEBP':
            save_kwargs['quality'] = quality

        img.save(buf, format=fmt, **save_kwargs)
        compressed_data = buf.getvalue()
        compressed_size = len(compressed_data)

        # Save to temp file
        output_filename = f'compressed_{uuid.uuid4().hex}.{ext}'
        output_path = Path(settings.TEMP_DIR) / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as out_file:
            out_file.write(compressed_data)

        savings_pct = round((1 - compressed_size / original_size) * 100, 1) if original_size > 0 else 0
        width, height = img.size

        return JsonResponse({
            'success': True,
            'filename': output_filename,
            'original_size': _format_size(original_size),
            'compressed_size': _format_size(compressed_size),
            'savings_percent': savings_pct,
            'dimensions': f'{width} × {height}',
            'format': fmt,
        })

    except Exception as e:
        return JsonResponse({'error': f'Compression failed: {str(e)}'}, status=500)



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
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.2f} MB'

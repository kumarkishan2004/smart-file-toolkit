"""
Views for PDF Compressor.
Compresses PDF by re-encoding images and removing redundant data.
"""
import uuid
import io
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404 ,HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


def index(request):
    """PDF Compressor tool page."""
    return render(request, 'pdf_compressor/index.html')


@require_POST
def compress(request):
    """Compress a PDF file by optimizing embedded images."""
    try:
        from pypdf import PdfWriter, PdfReader
        from PIL import Image

        f = request.FILES.get('pdf')
        quality = int(request.POST.get('quality', 60))
        quality = max(10, min(95, quality))  # Clamp 10-95

        if not f:
            return JsonResponse({'error': 'No PDF file uploaded.'}, status=400)
        if not f.name.lower().endswith('.pdf'):
            return JsonResponse({'error': 'Only PDF files are allowed.'}, status=400)
        if f.size > MAX_FILE_SIZE:
            return JsonResponse({'error': 'File exceeds 100MB limit.'}, status=400)

        original_size = f.size
        reader = PdfReader(f)

        if reader.is_encrypted:
            return JsonResponse({'error': 'Encrypted PDFs are not supported.'}, status=400)

        writer = PdfWriter()

        # Clone all pages
        for page in reader.pages:
            writer.add_page(page)

        # Compress images embedded in the PDF
        compressed_images = 0
        for page in writer.pages:
            if '/Resources' in page:
                resources = page['/Resources']
                if '/XObject' in resources:
                    xobjects = resources['/XObject']
                    for obj_name in list(xobjects.keys()):
                        xobj = xobjects[obj_name]
                        if xobj.get('/Subtype') == '/Image':
                            try:
                                data = xobj.get_data()
                                w = int(xobj['/Width'])
                                h = int(xobj['/Height'])
                                color_space = xobj.get('/ColorSpace', '/DeviceRGB')

                                # Determine PIL mode
                                if color_space in ('/DeviceRGB', '/RGB'):
                                    mode = 'RGB'
                                elif color_space in ('/DeviceGray', '/Gray'):
                                    mode = 'L'
                                else:
                                    mode = 'RGB'

                                img = Image.frombytes(mode, (w, h), data)
                                buf = io.BytesIO()
                                img.save(buf, format='JPEG', quality=quality, optimize=True)
                                compressed_data = buf.getvalue()

                                if len(compressed_data) < len(data):
                                    xobj._data = compressed_data
                                    xobj['/Filter'] = '/DCTDecode'
                                    xobj['/Length'] = len(compressed_data)
                                    compressed_images += 1
                            except Exception:
                                # Skip images that can't be compressed
                                pass

        # Write compressed PDF
        output_filename = f'compressed_{uuid.uuid4().hex}.pdf'
        output_path = Path(settings.TEMP_DIR) / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as out_file:
            writer.write(out_file)

        compressed_size = output_path.stat().st_size
        savings_pct = round((1 - compressed_size / original_size) * 100, 1) if original_size > 0 else 0
        # If compressed is actually larger, return original
        if compressed_size >= original_size:
            savings_pct = 0

        return JsonResponse({
            'success': True,
            'filename': output_filename,
            'original_size': _format_size(original_size),
            'compressed_size': _format_size(compressed_size),
            'savings_percent': savings_pct,
            'pages': len(reader.pages),
            'images_compressed': compressed_images,
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

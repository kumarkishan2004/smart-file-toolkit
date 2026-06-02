"""
Views for PDF Merger.
Merges multiple PDF files into one combined PDF.
"""
import uuid
import json
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404,HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render

ALLOWED_PDF_TYPE = 'application/pdf'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB per file
MAX_FILES = 20


def index(request):
    """PDF Merger tool page."""
    return render(request, 'pdf_merger/index.html')


@require_POST
def merge(request):
    """Merge multiple PDF files into one."""
    try:
        from pypdf import PdfWriter, PdfReader

        files = request.FILES.getlist('pdfs')

        if not files:
            return JsonResponse({'error': 'No PDF files uploaded.'}, status=400)
        if len(files) < 2:
            return JsonResponse({'error': 'Please upload at least 2 PDF files to merge.'}, status=400)
        if len(files) > MAX_FILES:
            return JsonResponse({'error': f'Maximum {MAX_FILES} files allowed.'}, status=400)

        writer = PdfWriter()
        total_pages = 0

        for f in files:
            # Accept both 'application/pdf' and 'application/octet-stream' for PDFs
            if not (f.name.lower().endswith('.pdf')):
                return JsonResponse({'error': f'Invalid file: {f.name}. Only PDF files allowed.'}, status=400)
            if f.size > MAX_FILE_SIZE:
                return JsonResponse({'error': f'File {f.name} exceeds 50MB limit.'}, status=400)
            try:
                reader = PdfReader(f)
                for page in reader.pages:
                    writer.add_page(page)
                total_pages += len(reader.pages)
            except Exception as e:
                return JsonResponse({'error': f'Could not read PDF: {f.name}. It may be corrupt or encrypted.'}, status=400)

        # Write merged PDF
        output_filename = f'merged_{uuid.uuid4().hex}.pdf'
        output_path = Path(settings.TEMP_DIR) / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as out_file:
            writer.write(out_file)

        file_size = output_path.stat().st_size
        return JsonResponse({
            'success': True,
            'filename': output_filename,
            'file_size': _format_size(file_size),
            'total_pages': total_pages,
            'files_merged': len(files),
        })

    except Exception as e:
        return JsonResponse({'error': f'Merge failed: {str(e)}'}, status=500)



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

# Smart File Toolkit

A full-stack Django web application providing professional file conversion and compression tools with a royal dark UI.

## Features

| Tool | Description |
|------|-------------|
| 📷 **Photo to PDF** | Convert JPG/PNG/WEBP/BMP images to a PDF document |
| 🔗 **PDF Merger** | Combine multiple PDFs into one (drag to reorder) |
| 📦 **PDF Compressor** | Reduce PDF file size by optimizing embedded images |
| 🖼️ **Image Compressor** | Compress images with a live quality slider |

## Tech Stack

- **Backend**: Django 4.2, Pillow, pypdf, reportlab
- **Frontend**: HTML5, CSS3 (custom royal dark theme), Vanilla JS
- **Design**: Cinzel + DM Sans fonts, glassmorphism, animated hero

---

## Quick Start

### 1. Clone / Extract the project

```bash
cd smart_file_toolkit
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

### 6. Open in browser

```
http://127.0.0.1:8000/
```

---

## Project Structure

```
smart_file_toolkit/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3                  ← auto-created on first run
│
├── smart_file_toolkit/         ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/                       ← Home, About, Contact pages
│   ├── views.py
│   └── urls.py
│
├── photo_to_pdf/               ← Photo → PDF feature
│   ├── views.py
│   └── urls.py
│
├── pdf_merger/                 ← PDF merging feature
│   ├── views.py
│   └── urls.py
│
├── pdf_compressor/             ← PDF compression feature
│   ├── views.py
│   └── urls.py
│
├── image_compressor/           ← Image compression feature
│   ├── views.py
│   └── urls.py
│
├── templates/                  ← All HTML templates
│   ├── base.html               ← Navbar, footer, toast system
│   ├── core/
│   │   ├── home.html           ← Dashboard with tool cards
│   │   ├── about.html
│   │   └── contact.html
│   ├── photo_to_pdf/index.html
│   ├── pdf_merger/index.html
│   ├── pdf_compressor/index.html
│   └── image_compressor/index.html
│
├── static/
│   ├── css/styles.css          ← Full royal dark theme
│   ├── js/main.js              ← Drag-drop, upload, toasts, animations
│   └── images/favicon.svg
│
└── media/
    └── temp/                   ← Processed files (auto-deleted)
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Home dashboard |
| GET | `/photo-to-pdf/` | Photo to PDF tool page |
| POST | `/photo-to-pdf/convert/` | Process images → PDF |
| GET | `/photo-to-pdf/download/<filename>/` | Download result |
| GET | `/pdf-merger/` | PDF Merger tool page |
| POST | `/pdf-merger/merge/` | Merge PDFs |
| GET | `/pdf-merger/download/<filename>/` | Download merged PDF |
| GET | `/pdf-compressor/` | PDF Compressor tool page |
| POST | `/pdf-compressor/compress/` | Compress PDF |
| GET | `/pdf-compressor/download/<filename>/` | Download compressed PDF |
| GET | `/image-compressor/` | Image Compressor tool page |
| POST | `/image-compressor/compress/` | Compress image |
| GET | `/image-compressor/download/<filename>/` | Download compressed image |

---

## File Limits

| Tool | File Types | Max Size | Max Files |
|------|-----------|----------|-----------|
| Photo to PDF | JPG, PNG, WEBP, GIF, BMP | 20 MB each | 20 images |
| PDF Merger | PDF | 50 MB each | 20 files |
| PDF Compressor | PDF | 100 MB | 1 file |
| Image Compressor | JPG, PNG, WEBP, BMP | 30 MB | 1 file |

---

## Production Deployment Notes

1. Change `SECRET_KEY` in `settings.py` to a secure random value
2. Set `DEBUG = False`
3. Set `ALLOWED_HOSTS` to your domain
4. Run `python manage.py collectstatic`
5. Use a production WSGI server (gunicorn, uWSGI)
6. Set up a cron job to clean old files in `media/temp/`

### Cleanup cron (Linux) — delete files older than 1 hour:
```bash
0 * * * * find /path/to/smart_file_toolkit/media/temp/ -type f -mmin +60 -delete
```

---

## Dependencies

```
Django==4.2.7          # Web framework
Pillow==10.1.0         # Image processing
pypdf==3.17.1          # PDF reading and manipulation
reportlab==4.0.8       # PDF generation from images
```

## License

Copyright © 2026 Your Name. All rights reserved.

This software and its documentation are proprietary and confidential. Unauthorized copying, modification, distribution, or use of this file, via any medium, is strictly prohibited.

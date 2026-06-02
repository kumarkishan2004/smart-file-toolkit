from django.shortcuts import render
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

@require_POST
def contact_submit(request):
    """Handle contact form submission and send email."""
    name    = request.POST.get('name', '').strip()
    email   = request.POST.get('email', '').strip()
    subject = request.POST.get('subject', 'general')
    message = request.POST.get('message', '').strip()

    if not all([name, email, message]):
        return JsonResponse({'error': 'All fields are required.'}, status=400)

    subject_labels = {
        'general': 'General Inquiry',
        'bug':     'Bug Report',
        'feature': 'Feature Request',
        'other':   'Other',
    }

    email_subject = f"[Smart File Toolkit] {subject_labels.get(subject, subject)} from {name}"
    email_body = f"""
New contact form message from Smart File Toolkit:

Name:    {name}
Email:   {email}
Subject: {subject_labels.get(subject, subject)}

Message:
{message}

---
Reply directly to: {email}
    """

    try:
        send_mail(
            subject=email_subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': f'Failed to send: {str(e)}'}, status=500)
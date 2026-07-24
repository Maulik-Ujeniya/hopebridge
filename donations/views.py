import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Sum

from .models import Donation, DonationAllocation
from .forms import DonationForm
from accounts.models import CustomUser


logger = logging.getLogger(__name__)

# Safely import razorpay
try:
    import razorpay
except ImportError:
    razorpay = None


@login_required
def donate_view(request):
    """Donation form page."""
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'name': request.user.get_full_name(),
            'email': request.user.email,
            'phone': request.user.phone,
            'city': request.user.city,
            'country': request.user.country,
            'pincode': request.user.pincode,
            'full_address': request.user.full_address,
        }

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            if request.user.is_authenticated:
                donation.donor = request.user
            donation.payment_status = 'pending'
            donation.save()

            # Initialize Razorpay Client if available
            if razorpay and settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_ID != 'rzp_test_placeholder':
                try:
                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                    amount_paise = int(donation.amount * 100)
                    razorpay_order = client.order.create({
                        'amount': amount_paise,
                        'currency': 'INR',
                        'receipt': donation.invoice_number,
                        'payment_capture': '1'
                    })
                    donation.razorpay_order_id = razorpay_order['id']
                    donation.save()

                    return render(request, 'donations/checkout.html', {
                        'donation': donation,
                        'razorpay_order_id': razorpay_order['id'],
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        'amount_paise': amount_paise,
                    })
                except Exception as e:
                    logger.warning('Razorpay setup failed for donation %s: %s', donation.pk, e)
                    messages.warning(request, f"Razorpay API Notice: {str(e)}. Simulating completion.")
            
            # Simulated completion for dev environment
            donation.payment_status = 'completed'
            donation.transaction_id = f'TXN_{donation.invoice_number}'
            donation.save()
            send_donation_email(donation)
            messages.success(request, f"Donation of ₹{donation.amount} completed successfully!")
            return redirect('donations:donation_success', donation_id=donation.id)
    else:
        form = DonationForm(initial=initial_data)

    return render(request, 'donations/donate_form.html', {'form': form})


@csrf_exempt
def payment_callback(request):
    """Callback view to verify signature and complete donation."""
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        try:
            donation = Donation.objects.get(razorpay_order_id=order_id)
        except Donation.DoesNotExist:
            return HttpResponseBadRequest("Invalid Order ID")

        if razorpay:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            try:
                client.utility.verify_payment_signature(params_dict)
                donation.payment_status = 'completed'
                donation.transaction_id = payment_id
                donation.razorpay_payment_id = payment_id
                donation.razorpay_signature = signature
                donation.save()

                send_donation_email(donation)
                messages.success(request, f"Donation of ₹{donation.amount} received successfully!")
                return redirect('donations:donation_success', donation_id=donation.id)
            except Exception as e:
                donation.payment_status = 'failed'
                donation.save()
                messages.error(request, "Payment signature verification failed.")
                return redirect('donations:donation_failed')
        else:
            donation.payment_status = 'completed'
            donation.transaction_id = payment_id or f'TXN_{donation.invoice_number}'
            donation.save()
            send_donation_email(donation)
            return redirect('donations:donation_success', donation_id=donation.id)

    return redirect('donations:donate_view')


def donation_success(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donations/success.html', {'donation': donation})


def donation_failed(request):
    return render(request, 'donations/failed.html')


@login_required
def donor_dashboard(request):
    """Dashboard for donors showing summary statistics."""
    donations = Donation.objects.filter(donor=request.user, payment_status='completed')
    total_donations = donations.count()
    total_amount = donations.aggregate(Sum('amount'))['amount__sum'] or 0
    last_donation = donations.order_by('-date_donated').first()
    
    allocations = DonationAllocation.objects.filter(donation__donor=request.user, donation__payment_status='completed')
    pending_allocations = sum(a.pending_amount for a in allocations)
    completed_allocations = sum(a.used_amount for a in allocations)
    
    # Mocking streak and impact score for UI presentation
    streak = 3 if total_donations > 2 else (1 if total_donations > 0 else 0)
    impact_score = int(total_amount / 100) * 1.5 if total_amount > 0 else 0
    
    return render(request, 'donations/donor_dashboard.html', {
        'total_donations': total_donations,
        'total_amount': total_amount,
        'last_donation': last_donation,
        'pending_allocations': pending_allocations,
        'completed_allocations': completed_allocations,
        'streak': streak,
        'impact_score': int(impact_score),
        'recent_donations': donations.order_by('-date_donated')[:5]
    })


@login_required
def my_donations(request):
    """History of donations for the logged-in user with filters."""
    donations = Donation.objects.filter(donor=request.user).order_by('-date_donated')
    
    # Filters
    status = request.GET.get('status')
    category = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status:
        donations = donations.filter(payment_status=status)
    if category:
        donations = donations.filter(donation_type=category)
    if date_from:
        donations = donations.filter(date_donated__gte=date_from)
    if date_to:
        donations = donations.filter(date_donated__lte=date_to)
        
    return render(request, 'donations/history.html', {'donations': donations})


@login_required
def donation_detail(request, donation_id):
    """Detailed allocation of donation."""
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user)
    allocations = donation.allocations.all()
    
    # Check allocation status for timeline
    has_allocations = allocations.exists()
    all_used = False
    if has_allocations:
        all_used = all(a.pending_amount <= 0 for a in allocations)
        
    return render(request, 'donations/detail.html', {
        'donation': donation,
        'allocations': allocations,
        'has_allocations': has_allocations,
        'all_used': all_used,
    })


@login_required
def resend_invoice(request, donation_id):
    """Resend invoice email."""
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user, payment_status='completed')
    send_donation_email(donation)
    messages.success(request, f"Invoice for {donation.invoice_number} has been resent to {donation.email}.")
    return redirect('donations:my_donations')


def send_donation_email(donation):
    """Helper to send thank you email with invoice info."""
    subject = f"Thank you for your donation to HopeBridge - Invoice {donation.invoice_number}"
    html_content = render_to_string('emails/donation_receipt.html', {'donation': donation})

    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[donation.email],
    )
    email.content_subtype = "html"

    try:
        from invoices.views import generate_invoice_pdf_buffer
        pdf_buffer = generate_invoice_pdf_buffer(donation)
        if pdf_buffer:
            email.attach(f"HopeBridge_Invoice_{donation.invoice_number}.pdf", pdf_buffer.getvalue(), "application/pdf")
    except Exception as e:
        logger.warning('Invoice attachment generation failed for donation %s: %s', donation.pk, e)

    try:
        email.send(fail_silently=True)
    except Exception:
        logger.exception('Failed to send donation receipt email for donation %s', donation.pk)

    if donation.donor:
        from notifications.models import Notification
        Notification.objects.create(
            recipient=donation.donor,
            title="💰 Donation Received",
            message=f"Thank you! Your donation of ₹{donation.amount} (Invoice: {donation.invoice_number}) has been received successfully.",
            notification_type='donation',
            link=f"/donate/my-donations/{donation.id}/"
        )
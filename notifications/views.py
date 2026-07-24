from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Notification


@login_required
def notification_list(request):
    """View all notifications with filters."""
    category_filter = request.GET.get('category', '')
    query = request.GET.get('q', '')
    
    # Exclude archived from main list unless explicitly requested
    notifications = Notification.objects.filter(recipient=request.user, is_archived=False)
    
    if category_filter:
        notifications = notifications.filter(category=category_filter)
    if query:
        notifications = notifications.filter(title__icontains=query) | notifications.filter(message__icontains=query)
        
    unread_count = notifications.filter(is_read=False).count()
    categories = Notification.CATEGORY_CHOICES

    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'category_filter': category_filter,
        'query': query,
        'unread_count': unread_count,
        'categories': categories,
    })


@login_required
def get_unread_notifications(request):
    """JSON endpoint to fetch unread notifications for the navbar dropdown."""
    unread = Notification.objects.filter(
        recipient=request.user, 
        is_read=False, 
        is_archived=False
    ).order_by('-created_at')[:5]
    
    count = Notification.objects.filter(
        recipient=request.user, 
        is_read=False, 
        is_archived=False
    ).count()
    
    data = []
    for notif in unread:
        data.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'category': notif.get_category_display(),
            'time_ago': notif.created_at.strftime('%b %d, %I:%M %p'),
            'link': notif.link
        })
        
    return JsonResponse({'count': count, 'notifications': data})


@login_required
def mark_read(request, notification_id):
    """Mark a single notification as read."""
    if request.method == 'POST':
        Notification.objects.filter(id=notification_id, recipient=request.user).update(is_read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def mark_all_read(request):
    """Mark all unread notifications as read."""
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def archive_notification(request, notification_id):
    """Archive a notification."""
    if request.method == 'POST':
        Notification.objects.filter(id=notification_id, recipient=request.user).update(is_archived=True)
        messages.success(request, "Notification archived.")
        return redirect('notifications:notification_list')
    return redirect('notifications:notification_list')


@login_required
def delete_notification(request, notification_id):
    """Permanently delete a notification."""
    if request.method == 'POST':
        Notification.objects.filter(id=notification_id, recipient=request.user).delete()
        messages.success(request, "Notification deleted.")
        return redirect('notifications:notification_list')
    return redirect('notifications:notification_list')

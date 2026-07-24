"""
Global context processors for HopeBridge.
Injects data available in all templates.
"""

import logging


logger = logging.getLogger(__name__)


def global_context(request):
    """Add global context variables to all templates."""
    context = {
        'site_name': 'HopeBridge',
        'site_tagline': 'Building Bridges of Hope',
    }

    # Add unread notification count for authenticated users
    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            context['unread_notifications_count'] = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
            context['latest_notifications'] = Notification.objects.filter(
                recipient=request.user
            ).order_by('-created_at')[:5]
        except Exception:
            logger.exception('Failed to load notification context for user %s', request.user.pk)
            context['unread_notifications_count'] = 0
            context['latest_notifications'] = []

    return context

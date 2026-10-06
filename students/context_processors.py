def student_context(request):
    """
    Context processor adding student profile, counts, and flags to templates.
    """
    context = {
        'student_profile': None,
        'unread_notifications_count': 0,
        'saved_count': 0,
        'applied_count': 0,
        'is_admin_user': False,
    }

    if request.user.is_authenticated:
        context['is_admin_user'] = request.user.is_staff or request.user.is_superuser
        try:
            profile = request.user.student_profile
            context['student_profile'] = profile
            context['unread_notifications_count'] = profile.notifications.filter(is_read=False).count()
            context['saved_count'] = profile.saved_opportunities.count()
            context['applied_count'] = profile.applications.count()
        except AttributeError:
            pass

    return context

# templatags/attendece_filters.py
from django import template

register = template.Library()

@register.filter
def filter_status(attendances, status):
    """
    Filtre les présences par statut
    """
    if not attendances:
        return []
    return [attendance for attendance in attendances if attendance.status == status]
from django import template
from django.utils.translation import ungettext, ugettext
import datetime

register = template.Library()

@register.filter(name='datetime_diff')
def datetime_diff(timestamp, to=None):
    if not timestamp:
        return ""
    
    compare_with = to or datetime.datetime.now()
    delta = timestamp - compare_with
    
    if delta.days == 0: return u"today"
    elif delta.days == -1: return u"yesterday"
    elif delta.days == 1: return u"tomorrow"
    
    chunks = (
        (365.0, lambda n: ungettext('year', 'years', n)),
        (30.0, lambda n: ungettext('month', 'months', n)),
        (7.0, lambda n : ungettext('week', 'weeks', n)),
        (1.0, lambda n : ungettext('day', 'days', n)),
        (0.04167, lambda n : ungettext('minute', 'minutes', n)),
        (.0000115741, lambda n : ungettext('second', 'seconds', n)),
    )
    
    for i, (chunk, name) in enumerate(chunks):
        if abs(delta.days) >= chunk:
            count = abs(round(delta.days / chunk, 0))
            break

    date_str = ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}
    
    if delta.days > 0: return "in " + date_str
    else: return date_str + " ago"

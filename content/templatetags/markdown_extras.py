from django import template
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt

register = template.Library()

# html=False is deliberate: it makes the renderer escape any literal HTML in the
# source (e.g. a writeup body containing "<script>...") instead of passing it
# through untouched, which is what keeps the mark_safe() below from becoming a
# stored-XSS hole.
_md = MarkdownIt('commonmark', {'html': False, 'typographer': True})


@register.filter(name='render_markdown')
def render_markdown(text):
    if not text:
        return ''
    return mark_safe(_md.render(text))

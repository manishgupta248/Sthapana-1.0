from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def sort_url(context, field):
    """Builds the web address for a clickable column heading — keeps all
    current filters/search intact, and flips the sort direction if you
    click the same column twice."""
    request = context["request"]
    current_sort = request.GET.get("sort", "")
    current_dir = request.GET.get("dir", "asc")
    new_dir = "desc" if current_sort == field and current_dir == "asc" else "asc"

    params = request.GET.copy()
    params["sort"] = field
    params["dir"] = new_dir
    return "?" + params.urlencode()


@register.simple_tag(takes_context=True)
def sort_indicator(context, field):
    """Shows a small up/down arrow next to whichever column is currently sorted."""
    request = context["request"]
    current_sort = request.GET.get("sort", "")
    current_dir = request.GET.get("dir", "asc")
    if current_sort != field:
        return ""
    return " ▲" if current_dir == "asc" else " ▼"
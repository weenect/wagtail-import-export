import json
from wagtail.core.models import Page


def export_pages(root_page, export_unpublished=False):
    pages = Page.objects.descendant_of(root_page, inclusive=True).order_by('path').specific()
    if not export_unpublished:
        pages = pages.filter(live=True)

    page_data = []
    exported_paths = set()
    for (i, page) in enumerate(pages):
        parent_path = page.path[:-(Page.steplen)]
        # skip over pages whose parents haven't already been exported
        # (which means that export_unpublished is false and the parent was unpublished)
        if i == 0 or (parent_path in exported_paths):
            page_data.append({
                'content': json.loads(page.to_json()),
                'model': page.content_type.model,
                'app_label': page.content_type.app_label,
            })
            exported_paths.add(page.path)
    return {
        'pages': page_data
    }
import json
import re

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ungettext, ugettext_lazy as _

import requests

from wagtailimportexport.compat import messages, Page
from wagtailimportexport.exporting import export_pages
from wagtailimportexport.forms import ExportForm, ImportFromAPIForm, ImportFromFileForm
from wagtailimportexport.importing import import_pages


def index(request):
    return render(request, 'wagtailimportexport/index.html')


def import_from_file(request):
    if request.method == 'POST':
        form = ImportFromFileForm(request.POST, request.FILES)
        if form.is_valid():
            import_file = form.cleaned_data['file']

            try:
                page_count = import_pages(import_file)
            except Exception as e:
                messages.error(request, _(
                    "Import failed: %(reason)s") % {'reason': e}
                )
            else:
                messages.success(request, ungettext(
                    "%(count)s page imported.",
                    "%(count)s pages imported.",
                    page_count) % {'count': page_count}
                )
            return redirect('wagtailimportexport_admin:index')
    else:
        form = ImportFromFileForm()

    return render(request, 'wagtailimportexport/import_from_file.html', {
        'form': form,
    })


def export_to_file(request):
    """
    Export a part of this source site's page tree to a ZIP file, according to
    the following specifications:

    - the ZIP file contains one .xls file per exported page
    - each .xls file is named `<page_model_name>-<page_id>.xls`
    - each .xls file contains data formatted this way:

        +------------+----------+-----------+-----------+--
        | Field name |    fr    |    en     |    de     |
        +------------+----------+-----------+-----------+--
        | title      | Le titre | The title | Der Titel |
        | body       | Le corps | The body  | Der Körper|
        +------------+----------+-----------+-----------+--
        |            |          |           |           |

    """
    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            payload_filename = export_pages(form.cleaned_data['root_page'], export_unpublished=True)
            response = HttpResponse(content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename="wagtail-export.zip"'
            with open(payload_filename, 'rb') as payload:
                response.write(payload.read())
            return response
    else:
        form = ExportForm()

    return render(request, 'wagtailimportexport/export_to_file.html', {
        'form': form,
    })

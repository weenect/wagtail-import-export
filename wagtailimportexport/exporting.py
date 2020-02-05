import zipfile

from wagtailimportexport.compat import Page


def export_pages(root_page, export_unpublished=False):
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

    Return the path to the created ZIP file.

    """
    pages = Page.objects.descendant_of(root_page, inclusive=True).order_by('path').specific()
    if not export_unpublished:
        pages = pages.filter(live=True)

    export_filename = 'wagtail-export.zip'

    with zipfile.ZipFile(export_filename, 'w') as export_zip:
        for page in pages:
            export_zip.write(page.export_translations())

    return export_filename

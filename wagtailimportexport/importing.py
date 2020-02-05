import glob
import tempfile
import zipfile

from django.conf import settings

from weeshop.apps.contents.multilingual import Multilingual


def import_pages(import_file):

    import_filenames = []
    num_processed_pages = 0

    with tempfile.TemporaryDirectory(dir=settings.UPLOAD_ROOT) as tmp_dir_name:

        # We check if this is an .xls file or a .zip one.
        content_type = import_file.content_type

        if 'excel' in content_type:

            # There is only one file to import.
            import_filenames.append(import_file.name)

        elif 'zip' in content_type:

            # We extract all the files from the archive and
            # add them to the list of files to import.
            with zipfile.ZipFile(import_file, 'r') as import_zip:
                import_zip.extractall(path=tmp_dir_name)
                import_filenames = glob.glob('%s/**/*.xls' % tmp_dir_name)

        # We can now process all files to import...
        for import_filename in import_filenames:
            try:
                Multilingual.import_translations(import_filename)
            except Exception as e:
                print(str(e))
                continue
            else:
                num_processed_pages += 1

    # ... and finally return the number of processed pages.
    return num_processed_pages

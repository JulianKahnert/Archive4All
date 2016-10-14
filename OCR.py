#!/usr/bin/env python3

import argparse
import glob
import os


def ocr_file(path_in, extension='pdf', rewrite_file=False, force_ocr=False, dirty_pdf=False):
    """
    Run OCR for one file

    Requirements:
    https://github.com/jbarlow83/OCRmyPDF/

    Parameters
    ----------
    path_in : string
        Path to a file, which should be reviewed

    Other Parameters
    ----------
    extension : string, optional
        File extension [png, jpeg, jpg, tiff, pdf], default: 'pdf'.
    rewrite_file : bool, optional
        Rewrite original PDF file with OCR PDF, default: False.
    force_ocr : bool, optional
        Force tesseract to rewrite OCR content.
    dirty_pdf : bool, optional
        Save original (not cleaned) version of the PDF file.

    Returns
    -------
    none

    """
    path_in = os.path.expanduser(os.path.normpath(path_in))
    # apply ocr on only one file
    if rewrite_file:
        path_out = path_in
    else:
        path_base = os.path.dirname(path_in)
        filename,_ = os.path.splitext(os.path.basename(path_in))
        path_out = path_base + '/' + filename + '_ocr.pdf'

    command = 'ocrmypdf --language deu+eng --rotate-pages --deskew --output-type pdfa --oversample 600 --clean '
    if not dirty_pdf:
        command += '--clean-final '
    if force_ocr:
        command += '--force-ocr '
    else:
        command += '--skip-text '

    command += '"{}" "{}"'.format(path_in, path_out)

    print(command)
    os.system(command)


def ocr_folder(path_in, extension='pdf', rewrite_file=False, force_ocr=True, dirty_pdf=False):
    """
    Run OCR for one file

    Requirements:
    https://github.com/jbarlow83/OCRmyPDF/

    Parameters
    ----------
    path_in : string
        Path to folder, which should be reviewed

    Other Parameters
    ----------
    extension : string, optional
        File extension [png, jpeg, jpg, tiff, pdf], default: 'pdf'.
    rewrite_file : bool, optional
        Rewrite original PDF file with OCR PDF, default: False.
    force_ocr : bool, optional
        Force tesseract to rewrite OCR content.
    dirty_pdf : bool, optional
        Save original (not cleaned) version of the PDF file.

    Returns
    -------
    none

    """
    path_in = os.path.expanduser(os.path.normpath(path_in)) + '/'
    # apply ocr on every file in path_in
    for file in glob.glob(path_in + '**/*.' + extension, recursive=True):
        ocr_file(path_in=file, extension=extension, rewrite_file=rewrite_file, force_ocr=force_ocr, dirty_pdf=dirty_pdf)


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(
        description='Commandline tool to generate searchable PDF files.')

    parser.add_argument('source',
                        action='store',
                        help='path to scanned file/folder with files')

    parser.add_argument('-ext', '--extension',
                        dest='extension',
                        action='store',
                        default='pdf',
                        help='destination of OCR PDFs [default: tiff]')

    parser.add_argument('-d', '--delete_old_file',
                        dest='delete_old_file',
                        action='store_true',
                        help='delete old file')

    parser.add_argument('-f', '--force_ocr',
                        dest='force_ocr',
                        action='store_true',
                        help='force tesseract to rewrite OCR content')

    parser.add_argument('-dpdf', '--dirty_pdf',
                        dest='save_dirty_pdf',
                        action='store_true',
                        help='not include the cleaned page in output')

    args = parser.parse_args()
    args.source = os.path.expanduser(os.path.normpath(args.source))

    if os.path.isfile(args.source):
        ocr_file(path_in=args.source, extension=args.extension, rewrite_file=args.delete_old_file, force_ocr=args.force_ocr, dirty_pdf=args.save_dirty_pdf)
    else:
        ocr_folder(path_in=args.source, extension=args.extension, rewrite_file=args.delete_old_file, force_ocr=args.force_ocr, dirty_pdf=args.save_dirty_pdf)


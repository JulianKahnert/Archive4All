#!/usr/bin/env python3

import glob
import os
from PyPDF2 import PdfFileMerger, PdfFileReader


base_path = os.path.dirname(os.path.realpath(__file__))

src_path = base_path + '/in/'
dst_path = base_path + '/out/'
file_list = glob.glob(src_path + '*.tiff')

# create PDF with OCR
for path in file_list:
    filename, ext = os.path.splitext(os.path.basename(path))
    command = 'ocrmypdf --rotate-pages --deskew --clean --clean-final --force-ocr --output-type pdfa  --oversample 600 "{}" "{}"'.format(
        src_path + filename + ext,
        dst_path + filename + '.pdf')
    print(command)
    os.system(command)

# combine front and back page
for front_idx in range(len(file_list) // 2):
    back_idx = len(file_list) - front_idx - 1
    print('combining: {} + {}'.format(front_idx, back_idx))

    front_path = dst_path + 'scan {}.pdf'.format(front_idx)
    back_path = dst_path + 'scan {}.pdf'.format(back_idx)

    front_pdf = PdfFileReader(open(front_path, 'rb'))
    back_pdf = PdfFileReader(open(back_path, 'rb'))

    merger = PdfFileMerger()
    merger.append(front_pdf)
    merger.append(back_pdf)
    merger.write(dst_path + 'scan_combined_{}.pdf'.format(front_idx))

    # delete old files
    os.system('rm "{}"'.format(front_path))
    os.system('rm "{}"'.format(back_path))

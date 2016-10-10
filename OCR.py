#!/usr/bin/env python3

import argparse
import glob
import os
from PyPDF2 import PdfFileMerger, PdfFileReader


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(
        description='Commandline tool to generate searchable PDF files.')

    parser.add_argument('-src', '--source',
                        dest='source',
                        action='store',
                        default=base_path + '/in/',
                        help='source of scanned files [default: REPO/in/]')

    parser.add_argument('-dst', '--destination',
                        dest='destination',
                        action='store',
                        default=base_path + '/out/',
                        help='destination of OCR PDFs [default: REPO/out/]')

    parser.add_argument('-ocr', '--ocr',
                        dest='ocr',
                        action='store_true',
                        help='run OCR')

    parser.add_argument('-c', '--combine',
                        dest='combine',
                        action='store_true',
                        help='combine front and back page to one pdf')

    parser.add_argument('-ext', '--extension',
                        dest='extension',
                        action='store',
                        default='tiff',
                        help='destination of OCR PDFs [default: tiff]')


    args = parser.parse_args()
    args.source = os.path.normpath(args.source) + '/'
    args.destination = os.path.normpath(args.destination) + '/'
    file_list = glob.glob(args.source + '*.' + args.extension)

    if args.ocr:
        if args.combine and not len(file_list) // 2 == len(file_list) / 2:
            raise RuntimeError('"{}" files found, this should be'.format(len(file_list)))

        # create PDF with OCR
        for path in file_list:
            filename, ext = os.path.splitext(os.path.basename(path))
            if filename == 'scan':
                os.system('mv "{}" "{}"'.format(args.source + 'scan' + ext, args.source + 'scan 0' + ext))
                filename = 'scan 0'

            command = 'ocrmypdf --rotate-pages --deskew --clean --clean-final --force-ocr --output-type pdfa  --oversample 600 "{}" "{}"'.format(
                args.source + filename + ext,
                args.destination + filename + '.pdf')
            
            print(command)
            os.system(command)

        if args.combine:
            # combine front and back page
            for front_idx in range(len(file_list) // 2):
                back_idx = len(file_list) - front_idx - 1
                print('combining: {} + {}'.format(front_idx, back_idx))

                front_path = args.destination + 'scan {}.pdf'.format(front_idx)
                back_path = args.destination + 'scan {}.pdf'.format(back_idx)

                front_pdf = PdfFileReader(open(front_path, 'rb'))
                back_pdf = PdfFileReader(open(back_path, 'rb'))

                merger = PdfFileMerger()
                merger.append(front_pdf)
                merger.append(back_pdf)
                merger.write(args.destination + 'scan_combined_{}.pdf'.format(front_idx))

                # delete old files
                os.system('rm "{}"'.format(front_path))
                os.system('rm "{}"'.format(back_path))


Toolkit for file tagging and archiving tasks.

This toolkit helps you to tag and archive files with this name convention (also see the [wiki](https://gitlab.com/JulianKahnert/Archiv4All/wikis/home)):
```
date--name__tag1_tag2_tagN.pdf
2016-01-07--apple-macbook__apple_bill.pdf
```

# Archive
### Onboarding
* install **tqdm** with `pip3 install tqdm`
* Generate new config file with `./archive.py --new-config`
* adjust the `./config.ini` file to fit your needs
* optional (needed for OCR tasks): [install ocrmypdf](https://ocrmypdf.readthedocs.io/en/latest/installation.html)
* optional (needed for macOS Finder tags): install **tag** with `brew install tag`

### Workflow
Requirement for `archive.py`: `pip3 install tqdm`

`./archive.py /PATH/TO/FILE/OR/FOLDER/`

* **year:** 2016 or 16 possible
* **name:** `capital letters, ' ', ä, ö, ü, ß` will be replaced
* **tags:**
    * select tag with number or write a new tag
    * finish tagging with empty input

### Maintenance of archive
* update macOS Finder tags: `maintenance.py --mac-tags`
* generate missing OCR: `maintenance.py --ocr`
* renew all OCR: `maintenance.py --ocr --force-ocr`
* show all OCR output: `maintenance.py --ocr --verbose`
* possible crontab entries:
```
@daily              /PATH/TO/Archive4All/maintenance.py --mac-tags &> /dev/null
0   4   1   *   *   /PATH/TO/Archive4All/maintenance.py --ocr &> /dev/null
```

-------

# OCR
```
ocrmypdf -l deu+eng --jobs 2 --rotate-pages --deskew --clean --clean-final --force-ocr --output-type pdfa  --oversample 600 SOURCE DESTINATION
```

### Installation on macOS
<https://ocrmypdf.readthedocs.io/en/latest/installation.html>
```
brew install libpng openjpeg jbig2dec libtiff     	# image libraries
brew install qpdf
brew install ghostscript
brew install python3
brew install libxml2 libffi leptonica
brew install unpaper
brew install tesseract --with-all-languages 		# nessasary for german language and "Umlaute"

pip3 install --upgrade pip
pip3 install ocrmypdf
```

### Installation on Ubuntu 16.04 (Xenial)

```
sudo apt install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng \
                 unpaper qpdf ghostscript

pip3 install --upgrade pip
pip3 install --user ocrmypdf
```

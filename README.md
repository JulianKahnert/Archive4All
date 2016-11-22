# ToDos

* skip file during workflow
* delete file during workflow
* optical improvements
* open pdf in background
* progress during file-tagging
* go a step back in workflow



# Archiv
## Workflow
`./Archiv4All.py /PATH/TO/FILE/OR/FOLDER/`

* **year:** 2016 or 16 possible
* **name:** `capital letters, ' ', ä, ö, ü, ß` will be changes
* **tags:**
    * select tag with number
    * write new tag (and save it to `config.ini`) with `:newtag`
    * finish tagging with empty input

# `config.ini` example
```
[dir]
archiv_path = ~/Downloads/test_archiv/

[tags]
tag1
tag2
tag3

```

# Update tags in config: `tag.py`
Requirement: `brew install tag`
```
./tags.py --help        # show this help message and exit
./tags.py --config      # update tags: Archiv => config.ini
./tags.py --mac-tags    # update macOS tags: Archiv => macOS Finder tags
```

-------

# OCR
```
ocrmypdf --jobs 2 --rotate-pages --deskew --clean --clean-final --force-ocr --output-type pdfa  --oversample 600 SOURCE DESTINATION
```

## Installation on macOS
<https://github.com/jbarlow83/OCRmyPDF#installing-on-mac-os-x>
```
brew install libpng openjpeg jbig2dec libtiff     	# image libraries
brew install qpdf
brew install ghostscript
brew install python3
brew install libxml2 libffi leptonica
brew install unpaper
brew install tesseract --with-all-languages 		# nessasary for german language and "Umlaute"

pip3 install --upgrade pip
pip3 install --upgrade pillow
pip3 install ocrmypdf
```

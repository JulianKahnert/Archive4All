Toolkit for file tagging and archiving tasks.

--------

# ToDos

* during workflow: skip/delete file
* during workflow: go one step back
* improve interface

--------

# Archiv
### Workflow
Requirement for `Archiv4All.py`: `pip3 install tqdm`
`./Archiv4All.py /PATH/TO/FILE/OR/FOLDER/`

* **year:** 2016 or 16 possible
* **name:** `capital letters, ' ', ä, ö, ü, ß` will be replaced
* **tags:**
    * select tag with number
    * write new tag (and save it to `config.ini`) with `:newtag`
    * finish tagging with empty input

### Update tags in config: `tag.py`
Requirement for `tag.py`: `brew install tag`
```
./tags.py --help        # show this help message and exit
./tags.py --config      # update tags: Archiv => config.ini
./tags.py --mac-tags    # update macOS tags: Archiv => macOS Finder tags
```

### `config.ini` example
```
[dir]
archiv_path = ~/Downloads/test_archiv/

[tags]
tag1
tag2
tag3

```

-------

# OCR
```
ocrmypdf -l deu+eng --jobs 2 --rotate-pages --deskew --clean --clean-final --force-ocr --output-type pdfa  --oversample 600 SOURCE DESTINATION
```

### Installation on macOS
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

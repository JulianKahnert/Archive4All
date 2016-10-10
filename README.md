# ToDo
* OCR-only mode => just add OCR to existing PDFs
* only OCR, if pdf does not already have it + force write option
* test german "Umlaute"

```
ocrmypdf --jobs 2 --rotate-pages --deskew --clean --clean-final --force-ocr --output-type pdfa  --oversample 600 SOURCE DESTINATION
```

# Installation on macOS
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
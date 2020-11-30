import pytesseract

image = "./_misc/sample.png"
text = pytesseract.image_to_string(image, lang="eng")

print("="*80)
print(text)
print("="*80)
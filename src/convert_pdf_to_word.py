from pathlib import Path
from pdf2docx import Converter

pdf_file = 'xpwc.pdf'

file_path = Path( pdf_file).expanduser()  # Expand user directory if '~' is used
print(file_path.resolve())
word_file = 'output.docx'

cv = Converter(pdf_file)
cv.convert(word_file)
cv.close()
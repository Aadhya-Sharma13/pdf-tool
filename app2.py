from flask import Flask, request, send_file, render_template, jsonify
import subprocess
import os
from pathlib import Path
import tempfile
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

app = Flask(__name__)

# --- Configuration Paths (Linux Environment) ---
GHOSTSCRIPT_PATH = Path("/usr/bin/gs")
PYTESSERACT_PATH = Path("/usr/bin/tesseract")
POPPLER_PATH = Path("/usr/bin")  # Path where pdftoppm and other utilities are available

# Assign tesseract command path
pytesseract.pytesseract.tesseract_cmd = str(PYTESSERACT_PATH)

# --- Upload Folder ---
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# --- Helper Functions ---
def compress_pdf_ghostscript(input_path, output_path):
    """Compresses a PDF file using Ghostscript."""
    try:
        subprocess.run([
            str(GHOSTSCRIPT_PATH), "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={output_path}",
            str(input_path)
        ], check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"❌ Ghostscript error: {e}")
        return False

def ocr_pdf(input_path, output_path):
    """Performs OCR on a PDF."""
    try:
        images = convert_from_path(input_path, poppler_path=str(POPPLER_PATH))
        temp_dir = Path(tempfile.gettempdir())
        output_pdfs = []

        for i, image in enumerate(images):
            page_output_pdf = temp_dir / f"page_{i+1}_ocr.pdf"
            page_data = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
            with open(page_output_pdf, 'wb') as f:
                f.write(page_data)
            output_pdfs.append(page_output_pdf)

        subprocess.run([
            str(GHOSTSCRIPT_PATH), "-sDEVICE=pdfwrite",
            "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={output_path}",
            *[str(p) for p in output_pdfs]
        ], check=True)

        for p in output_pdfs:
            os.remove(p)

        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"❌ OCR processing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'pdf' not in request.files or 'operation' not in request.form:
        return jsonify({"error": "Missing file or operation"}), 400

    file = request.files['pdf']
    operation = request.form['operation']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    input_pdf_path = UPLOAD_FOLDER / file.filename
    output_pdf_name = f"{operation}_{file.filename}"
    output_pdf_path = UPLOAD_FOLDER / output_pdf_name

    file.save(input_pdf_path)
    original_size = os.path.getsize(input_pdf_path)

    success = False
    if operation == 'compress':
        success = compress_pdf_ghostscript(input_pdf_path, output_pdf_path)
    elif operation == 'ocr':
        success = ocr_pdf(input_pdf_path, output_pdf_path)
    else:
        return jsonify({"error": "Invalid operation"}), 400

    if success and output_pdf_path.exists():
        processed_size = os.path.getsize(output_pdf_path)
        return jsonify({
            "download_url": f"/download/{output_pdf_name}",
            "original_size": original_size,
            "processed_size": processed_size
        }), 200
    else:
        return jsonify({"error": f"Operation '{operation}' failed"}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = UPLOAD_FOLDER / filename
        if not file_path.exists() or not file_path.resolve().is_relative_to(UPLOAD_FOLDER.resolve()):
            return "File not found.", 404

        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

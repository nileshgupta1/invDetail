import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin   
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import easyocr
import cv2
import json
import google.generativeai as genai

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_image(image_path):
    reader = easyocr.Reader(['en'])
    image = cv2.imread(image_path)
    results = reader.readtext(image)

    extracted_text = []
    for (bbox, text, prob) in results:
        extracted_text.append(text)

    return '. '.join(extracted_text)

def extract_invoice_details(text):
    prompt = f"""
    Extract the following details from the invoice text and format them as a valid JSON object:
    1. Customer details
    2. Products
    3. Total Amount

    Provide the output in JSON format with the following structure without any unwanted characters like backslash:
    {{
        "customer_details": "",
        "products": [],
        "total_amount": ""
    }}

    If any information is not available, use null for missing string values, 0 for missing numeric values, or an empty array [] for missing lists.

    Invoice text:
    {text}

    Respond only with the valid JSON object, nothing else.
    """

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"raw_response": response.text}

@app.route('/process_invoice', methods=['POST'])
def process_invoice():
    if 'file' not in request.files:
        return jsonify({"error": "No file found in the request"})
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            # print(text)
        else:
            text = extract_text_from_image(file_path)
        
        invoice_details = extract_invoice_details(text)
        os.remove(file_path) 
        return jsonify(invoice_details)

    return jsonify({"error": "Invalid file type"})

if __name__ == '__main__':
    app.run(debug=True)



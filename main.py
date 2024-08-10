import os
from dotenv import load_dotenv
import openai
from PyPDF2 import PdfReader
import json

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def extractTextFromPdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extractInvoiceDetails(text):
    prompt = f"""
    Extract the following details from the invoice text:
    1. Customer details
    2. Products
    3. Total Amount

    Provide the output in JSON format with the following structure:
    {{
        "customer_details": "",
        "products": [],
        "total_amount": ""
    }}

    Invoice text:
    {text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts information from a given invoice."},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message['content'])

def processInvoice(pdf_path):
    text = extractTextFromPdf(pdf_path)
    # print(text)
    invoice_details = extractInvoiceDetails(text)
    return invoice_details

if __name__ == "__main__":
    pdf_path = "./invoice.pdf"
    invoice_details = processInvoice(pdf_path)
    print(json.dumps(invoice_details, indent=2))

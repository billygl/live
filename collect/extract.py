import os
from PIL import Image
import pytesseract
import re
from dotenv import load_dotenv

from google import genai
import json

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

data_dir = 'data'

def extract_info(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    with open('output.txt', 'a', encoding='utf-8') as f:
        f.write(f"--- {os.path.basename(image_path)} ---\n{text}\n")
    # Extract date (formats: YYYY-MM-DD, DD/MM/YYYY, etc.)
    date_match = re.search(r'(\d{4}[\.-/]\d{2}[\.-/]\d{2}|\d{2}[\.-/]\d{2}[\.-/]\d{4}|\d{2}[\.-/]\d{2}[\.-/]\d{4})', text)
    # Extract kilometers (formats: 123456 km, 123,456km, etc.)
    km_match = re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,3})?)\s*km', text, re.IGNORECASE)
    date = date_match.group(0) if date_match else None
    kilometers = km_match.group(1).replace(',', '').replace('.', '') if km_match else None
    return date, kilometers


def extract_vlm(image_path):
    client = genai.Client(api_key=API_KEY)

    my_file = client.files.upload(file=image_path)
    
    model = 'models/gemma-3-27b-it'
    my_prompt = "Extract the date and odometer in kilometers from the following image in json format. The extracted date is day, month, year, but the ouput date should be in YYYY-MM-dd."
    response = client.models.generate_content(
        model=model, 
        contents=[my_file, my_prompt]
    )
    with open('output.txt', 'a', encoding='utf-8') as f:
        f.write(f"### {os.path.basename(image_path)} ###\n{response.text}\n")
    try:
        json_text = response.text[response.text.index('{'):-3]
        result = json.loads(json_text)
        date = result.get('date')
        kilometers = result.get('odometer_km')
    except Exception as e:
        print(e)
        date = None
        kilometers = None
    return date, kilometers

def main():
    for root, _, files in os.walk(data_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(root, filename)
                date, km = extract_info(path)
                print(f"{os.path.relpath(path, data_dir)}: Date={date}, Kilometers={km}")
                #TODO improve when it is an array
                date, km = extract_vlm(path)

                print(f"{os.path.relpath(path, data_dir)}:: Date={date}, Kilometers={km}")


main()

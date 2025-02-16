from flask import Flask, request, send_file
from rembg import remove
from PIL import Image
import requests
import io
import os

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_image():
    data = request.json
    headers = {
        "Authorization": f"Bearer {os.getenv('STABILITY_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text_prompts": [{"text": data['prompt']}],
        "cfg_scale": 7,
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }
    
    response = requests.post(
        "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        return "Error", 500
    
    image_data = response.json()['artifacts'][0]['base64']
    return send_file(io.BytesIO(image_data), 200, {'Content-Type': 'image/png'})

@app.route('/sticker', methods=['POST'])
def make_sticker():
    image = request.files['image'].read()
    
    # Remove background
    cleaned = remove(image)
    
    # Resize and format
    img = Image.open(io.BytesIO(cleaned))
    img.thumbnail((512, 512))
    
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    
    return send_file(output, mimetype='image/png')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

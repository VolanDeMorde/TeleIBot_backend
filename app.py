from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Mock AI functions (replace with actual implementations)
def generate_image_with_ai(prompt):
    # Replace with your AI model (e.g., Stable Diffusion)
    return b"mock_image_bytes"

def create_sticker(image_bytes):
    # Replace with your sticker creation logic
    return b"mock_sticker_bytes"

def inpaint_image(image_bytes, prompt):
    # Replace with your inpainting logic
    return b"mock_inpainted_image_bytes"

# Generate Image Endpoint
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    image_bytes = generate_image_with_ai(prompt)
    return send_file(io.BytesIO(image_bytes), mimetype='image/png')

# Create Sticker Endpoint
@app.route('/sticker', methods=['POST'])
def sticker():
    if 'image' not in request.files:
        return jsonify({"error": "Image is required"}), 400
    
    image = request.files['image']
    image_bytes = image.read()
    
    sticker_bytes = create_sticker(image_bytes)
    return send_file(io.BytesIO(sticker_bytes), mimetype='image/png')

# Inpaint Image Endpoint
@app.route('/inpaint', methods=['POST'])
def inpaint():
    if 'image' not in request.files:
        return jsonify({"error": "Image is required"}), 400
    
    image = request.files['image']
    prompt = request.form.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    image_bytes = image.read()
    inpainted_bytes = inpaint_image(image_bytes, prompt)
    return send_file(io.BytesIO(inpainted_bytes), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

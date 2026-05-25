from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
from pathlib import Path
import torch

# Add model folder to path
sys.path.insert(0, str(Path(__file__).parent / 'model'))

# Import from your existing v1 code
from model import RPGItemGPT, block_size, device

app = Flask(__name__)
CORS(app)  # Allow requests from React app

# ============================================================================
# TOKENIZER (from your v1 code)
# ============================================================================

class CharTokenizer:
    """Simple character-level tokenizer."""
    
    def __init__(self, chars):
        self.chars = chars
        self.vocab_size = len(self.chars)
        self.stoi = {ch: i for i, ch in enumerate(self.chars)}
        self.itos = {i: ch for i, ch in enumerate(self.chars)}
    
    def encode(self, s):
        return [self.stoi[c] for c in s]
    
    def decode(self, l):
        return ''.join([self.itos[i] for i in l])

# ============================================================================
# LOAD MODEL
# ============================================================================

def load_model(checkpoint_path='trained_models/final_model.pt'):
    """Load trained model from checkpoint."""
    print(f"Loading model from {checkpoint_path}...")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Recreate tokenizer
    tokenizer = CharTokenizer(checkpoint['tokenizer_chars'])
    
    # Create and load model
    model = RPGItemGPT(tokenizer.vocab_size).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"Model loaded successfully!")
    print(f"Device: {device}")
    print(f"Vocabulary size: {tokenizer.vocab_size}")
    
    return model, tokenizer

# Initialize model once at startup
print("\n" + "="*80)
print("Starting RPG Item Generator API v1...")
print("="*80)

MODEL_PATH = 'trained_models/final_model.pt'
model, tokenizer = load_model(MODEL_PATH)

print("API ready!")
print("="*80 + "\n")

# ============================================================================
# GENERATION FUNCTIONS
# ============================================================================

def generate_item(temperature=0.8, top_k=50, max_length=150):
    """Generate a single RPG item."""
    # Start with opening bracket
    context = torch.tensor([tokenizer.encode('[')], dtype=torch.long, device=device)
    
    # Generate
    with torch.no_grad():
        generated = model.generate(context, max_new_tokens=max_length, 
                                  temperature=temperature, top_k=top_k)
    
    # Decode
    generated_text = tokenizer.decode(generated[0].tolist())
    
    # Extract just the item (until newline)
    item = generated_text.split('\n')[0] if '\n' in generated_text else generated_text
    
    return item

def parse_item(item_text):
    """Parse item text into structured format."""
    try:
        # Extract rarity
        rarity_match = item_text.split(']')[0].replace('[', '')
        
        # Split by pipes
        parts = item_text.split('|')
        
        # Extract components
        name_part = parts[0].split(']')[-1].strip() if len(parts) > 0 else ""
        item_type = parts[1].strip() if len(parts) > 1 else "unknown"
        
        # Extract stats (everything except last part with quotes)
        stats = []
        for i in range(2, len(parts)):
            part = parts[i].strip()
            if not part.startswith('"'):
                stats.append(part)
        
        # Extract flavor
        flavor = ""
        for part in parts:
            if '"' in part:
                flavor = part.strip(' "')
                break
        
        return {
            'text': item_text,
            'rarity': rarity_match,
            'name': name_part,
            'type': item_type,
            'stats': stats,
            'flavor': flavor
        }
    except Exception as e:
        return {
            'text': item_text,
            'rarity': 'UNKNOWN',
            'name': '',
            'type': 'unknown',
            'stats': [],
            'flavor': '',
            'parse_error': str(e)
        }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/generate', methods=['GET', 'POST'])
def api_generate_items():
    """Generate items endpoint."""
    try:
        # Get parameters
        if request.method == 'POST':
            data = request.json
            num_items = data.get('num', 10)
            temperature = data.get('temperature', 0.8)
            rarity = data.get('rarity', None)
        else:
            num_items = int(request.args.get('num', 10))
            temperature = float(request.args.get('temperature', 0.8))
            rarity = request.args.get('rarity', None)
        
        # Limit to prevent abuse
        num_items = min(num_items, 100)
        
        print(f"Generating {num_items} items (temp={temperature}, rarity={rarity})...")
        
        # Generate items
        items = []
        attempts = 0
        max_attempts = num_items * 3  # Try up to 3x for rarity filtering
        
        while len(items) < num_items and attempts < max_attempts:
            attempts += 1
            item_text = generate_item(temperature=temperature, max_length=150)
            
            # Filter by rarity if specified
            if rarity and rarity.upper() in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY']:
                if f'[{rarity.upper()}]' in item_text:
                    items.append(item_text)
            else:
                items.append(item_text)
        
        # Parse items
        parsed_items = [parse_item(item) for item in items]
        
        print(f"Generated {len(items)} items successfully")
        
        return jsonify({
            'success': True,
            'items': parsed_items,
            'count': len(items)
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'version': 'v1',
        'model_loaded': model is not None
    })

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get model statistics."""
    return jsonify({
        'vocab_size': tokenizer.vocab_size,
        'device': str(device),
        'version': 'v1'
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("RPG Item Generator API Server v1")
    print("="*80)
    print("\nEndpoints:")
    print("  GET  /api/health          - Check if API is running")
    print("  GET  /api/stats           - Get model statistics")
    print("  GET  /api/generate        - Generate items")
    print("       ?num=10              - Number of items (max 100)")
    print("       &temperature=0.8     - Sampling temperature")
    print("       &rarity=LEGENDARY    - Filter by rarity (optional)")
    print("\nExamples:")
    print("  http://localhost:5000/api/generate?num=10")
    print("  http://localhost:5000/api/generate?num=5&rarity=LEGENDARY")
    print("  http://localhost:5000/api/generate?num=20&temperature=1.2")
    print("\n" + "="*80)
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*80 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

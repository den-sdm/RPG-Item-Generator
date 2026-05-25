RPG ITEM GENERATOR

GPT-style transformer that generates fantasy RPG items with stats, rarities, and flavor text.

================================================================================
REQUIREMENTS
================================================================================

- Python 3.11+
- PyTorch
- Flask and flask-cors (for web interface)
- Node.js and npm (for web interface)

================================================================================
TRAINING
================================================================================

USING COLAB (RECOMMENDED)

Takes 1.5-2.5 hours on GPU.

1. Open the Colab notebook in colab/ folder
2. Upload dataset/synthetic_items.txt
3. Run all cells
4. Download best_model.pt and final_model.pt
5. Put models in trained_models/ folder

USING COMMAND LINE

Takes 15-20 hours on CPU. Not recommended.

    cd model
    py train.py --dataset ../dataset/synthetic_items.txt

================================================================================
GENERATING ITEMS
================================================================================

WEB INTERFACE

Terminal 1 - Start API:
    py api_server_v1.py

Terminal 2 - Start UI:
    cd demo-ui
    npm start

Browser opens at localhost:3000. Click generate, adjust temperature and filters.

COMMAND LINE

Non-interactive:
    cd model
    py generate.py --checkpoint ../trained_models/final_model.pt --num 10
    py generate.py --checkpoint ../trained_models/final_model.pt --num 20 --temperature 1.2
    py generate.py --checkpoint ../trained_models/final_model.pt --num 10 --rarity RARE

Interactive mode:
    py generate.py --checkpoint ../trained_models/final_model.pt --interactive

You'll be asked for number of items, temperature, and optional rarity filter.

================================================================================
EXAMPLE OUTPUT
================================================================================

[LEGENDARY] Void Crusher of the Damned | weapon-dagger | DMG: 156-234 | +67 INT | +23% Cast Speed | "The blade whispers secrets of the void."

[EPIC] Thunder Bulwark | armor-chest | ARM: 184 | +193 STR | +82 DEX | +87 Max Life | "Protected demonic forces from death."

[RARE] Abyssal Bane | weapon-bow | DMG: 21-39 | +85 DEX | +33% Projectile Speed | "Forged in the fires of death itself."

[COMMON] Rusty Sword | weapon-sword | DMG: 12-18 | "A weathered blade, better than nothing."

================================================================================
PROJECT STRUCTURE
================================================================================

RPG-Item-Generator/
├── dataset/
│   └── synthetic_items.txt      # 10,000 training items
├── model/
│   ├── model.py                 # GPT architecture
│   ├── train.py                 # Training script
│   └── generate.py              # Generation script
├── trained_models/
│   ├── best_model.pt           # Best model checkpoint
│   └── final_model.pt          # Final model
├── demo-ui/                    # React web interface
├── api_server_v1.py            # Flask backend
└── README.txt

================================================================================
TECHNICAL DETAILS
================================================================================

- Architecture: 6-layer transformer, 6 attention heads, 384 embedding dimensions
- Parameters: 7.5M trainable
- Context window: 256 characters
- Tokenization: Character-level
- Optimizer: AdamW

================================================================================
TROUBLESHOOTING
================================================================================

Model not found:
    dir trained_models\*.pt
    py generate.py --checkpoint "D:\full\path\to\final_model.pt"

API won't start:
    pip install flask flask-cors

UI won't load:
    cd demo-ui
    npm install
    npm start
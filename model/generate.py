import torch
from model import RPGItemGPT, block_size, device
import argparse
from tqdm import tqdm


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


def load_model(checkpoint_path='best_model.pt'):
    """Load a trained model from checkpoint."""
    checkpoint = torch.load(checkpoint_path, map_location=device)

    # Recreate tokenizer
    tokenizer = CharTokenizer(checkpoint['tokenizer_chars'])

    # Create and load model
    model = RPGItemGPT(tokenizer.vocab_size).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    print(f"Model loaded from {checkpoint_path}")
    print(f"Vocabulary size: {tokenizer.vocab_size}")

    return model, tokenizer


def generate_item(model, tokenizer, temperature=0.8, top_k=50, max_length=300):
    """Generate a single RPG item."""
    # Start with opening bracket
    context = torch.tensor([tokenizer.encode('[')], dtype=torch.long, device=device)

    # Generate
    with torch.no_grad():
        generated = model.generate(context, max_new_tokens=max_length, temperature=temperature, top_k=top_k)

    # Decode
    generated_text = tokenizer.decode(generated[0].tolist())

    # Extract just the item (until newline)
    item = generated_text.split('\n')[0] if '\n' in generated_text else generated_text

    return item


def generate_batch(model, tokenizer, num_items=10, temperature=0.8, rarity_filter=None):
    """Generate multiple items with progress bar."""
    items = []
    attempts = 0
    max_attempts = num_items * 3
    
    # Create progress bar
    pbar = tqdm(total=num_items, desc="Generating items", unit="item", 
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
    
    while len(items) < num_items and attempts < max_attempts:
        attempts += 1
        item = generate_item(model, tokenizer, temperature=temperature)
        
        # Filter by rarity if specified
        if rarity_filter:
            if f'[{rarity_filter}]' in item:
                items.append(item)
                pbar.update(1)  # Update progress bar
        else:
            items.append(item)
            pbar.update(1)  # Update progress bar
    
    pbar.close()  # Close progress bar
    return items

def interactive_mode(model, tokenizer):
    """Interactive item generation."""
    print("\n" + "=" * 80)
    print("RPG ITEM GENERATOR - Interactive Mode")
    print("=" * 80)
    print("\nCommands:")
    print("  <number>     - Generate that many items (e.g., '5')")
    print("  temp <0-2>   - Set temperature (default 0.8)")
    print("  rarity <R>   - Filter by rarity (COMMON/UNCOMMON/RARE/EPIC/LEGENDARY)")
    print("  clear        - Clear rarity filter")
    print("  quit         - Exit")
    print()

    temperature = 0.8
    rarity_filter = None

    while True:
        try:
            command = input(">>> ").strip().lower()

            if command == 'quit':
                print("Goodbye!")
                break

            elif command.startswith('temp '):
                try:
                    temp = float(command.split()[1])
                    if 0 < temp <= 2:
                        temperature = temp
                        print(f"Temperature set to {temperature}")
                    else:
                        print("Temperature must be between 0 and 2")
                except:
                    print("Invalid temperature. Usage: temp <0-2>")

            elif command.startswith('rarity '):
                rarity = command.split()[1].upper()
                if rarity in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY']:
                    rarity_filter = rarity
                    print(f"Filtering for {rarity} items")
                else:
                    print("Invalid rarity. Options: COMMON/UNCOMMON/RARE/EPIC/LEGENDARY")

            elif command == 'clear':
                rarity_filter = None
                print("Rarity filter cleared")

            elif command.isdigit():
                num_items = int(command)
                if num_items > 50:
                    print("Maximum 50 items at once")
                    continue

                print(f"\nGenerating {num_items} items...")
                items = generate_batch(model, tokenizer, num_items, temperature, rarity_filter)

                print("\n" + "-" * 80)
                for i, item in enumerate(items, 1):
                    print(f"{i}. {item}")
                print("-" * 80 + "\n")

            else:
                print("Unknown command. Type a number to generate items, or 'quit' to exit.")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Generate RPG items')
    parser.add_argument('--checkpoint', type=str, default='final_model.pt',
                        help='Path to model checkpoint')
    parser.add_argument('--num', type=int, default=10,
                        help='Number of items to generate (if not interactive)')
    parser.add_argument('--temperature', type=float, default=0.8,
                        help='Sampling temperature')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode')

    args = parser.parse_args()

    # Load model
    model, tokenizer = load_model(args.checkpoint)

    if args.interactive:
        interactive_mode(model, tokenizer)
    else:
        # Generate items
        print(f"\nGenerating {args.num} items with temperature {args.temperature}...\n")
        items = generate_batch(model, tokenizer, args.num, args.temperature)

        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")


if __name__ == '__main__':
    main()
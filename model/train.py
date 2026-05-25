import torch
import torch.nn as nn
from torch.nn import functional as F
import time
import os
import argparse
from model import RPGItemGPT, batch_size, block_size, learning_rate, max_iters, eval_interval, eval_iters, device


# Data loading
def load_data(filepath='synthetic_items.txt'):
    """Load the dataset from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"Dataset loaded: {len(text):,} characters")
    return text


# Character-level tokenization
class CharTokenizer:
    """Simple character-level tokenizer."""

    def __init__(self, text):
        self.chars = sorted(list(set(text)))
        self.vocab_size = len(self.chars)
        self.stoi = {ch: i for i, ch in enumerate(self.chars)}
        self.itos = {i: ch for i, ch in enumerate(self.chars)}
        print(f"Vocabulary size: {self.vocab_size} characters")
        print(f"Characters: {''.join(self.chars[:50])}...")

    def encode(self, s):
        """Convert string to list of integers."""
        return [self.stoi[c] for c in s]

    def decode(self, l):
        """Convert list of integers to string."""
        return ''.join([self.itos[i] for i in l])


def get_batch(data, batch_size, block_size):
    """Generate a small batch of data of inputs x and targets y."""
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i + block_size] for i in ix])
    y = torch.stack([data[i + 1:i + block_size + 1] for i in ix])
    x, y = x.to(device), y.to(device)
    return x, y


@torch.no_grad()
def estimate_loss(model, train_data, val_data, eval_iters):
    """Estimate loss on train and val sets."""
    out = {}
    model.eval()
    for split, data in [('train', train_data), ('val', val_data)]:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(data, batch_size, block_size)
            logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out


def train(model, train_data, val_data, optimizer, max_iters, eval_interval, eval_iters):
    """Training loop."""
    print("\nStarting training...")
    print(f"Device: {device}")
    print(f"Batch size: {batch_size}")
    print(f"Block size: {block_size}")
    print(f"Max iterations: {max_iters}")

    start_time = time.time()
    best_val_loss = float('inf')

    for iter in range(max_iters):
        # Evaluate periodically
        if iter % eval_interval == 0 or iter == max_iters - 1:
            losses = estimate_loss(model, train_data, val_data, eval_iters)
            elapsed = time.time() - start_time
            print(
                f"Step {iter:4d} | Train loss: {losses['train']:.4f} | Val loss: {losses['val']:.4f} | Time: {elapsed:.1f}s")

            # Save best model
            if losses['val'] < best_val_loss:
                best_val_loss = losses['val']
                torch.save({
                    'iter': iter,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_loss': losses['val'],
                }, 'best_model.pt')
                print(f"  → Saved best model (val loss: {best_val_loss:.4f})")

        # Sample a batch
        xb, yb = get_batch(train_data, batch_size, block_size)

        # Forward pass
        logits, loss = model(xb, yb)

        # Backward pass
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    total_time = time.time() - start_time
    print(f"\nTraining complete! Total time: {total_time / 60:.1f} minutes")
    print(f"Best validation loss: {best_val_loss:.4f}")


def generate_sample_items(model, tokenizer, num_items=5, max_length=300, temperature=0.8):
    """Generate sample items from the model."""
    print(f"\n{'=' * 80}")
    print("SAMPLE GENERATED ITEMS")
    print(f"{'=' * 80}\n")

    model.eval()

    for i in range(num_items):
        # Start with opening bracket for item format
        context = torch.tensor([tokenizer.encode('[')], dtype=torch.long, device=device)

        # Generate
        generated = model.generate(context, max_new_tokens=max_length, temperature=temperature, top_k=50)
        generated_text = tokenizer.decode(generated[0].tolist())

        # Try to extract just the item (until newline)
        item = generated_text.split('\n')[0] if '\n' in generated_text else generated_text

        print(f"{i + 1}. {item}")
        print()

    model.train()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train RPG Item Generator')
    parser.add_argument('--dataset', type=str, default='synthetic_items.txt',
                        help='Path to training dataset (default: synthetic_items.txt)')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Directory to save models (default: current directory)')
    args = parser.parse_args()

    print("=" * 80)
    print("RPG ITEM GENERATOR - TRAINING")
    print("=" * 80)
    print(f"Dataset: {args.dataset}")
    print(f"Output directory: {args.output_dir}")
    print(f"Using device: {device}")
    print("=" * 80)

    # Load data
    text = load_data(args.dataset)

    # Create tokenizer
    tokenizer = CharTokenizer(text)

    # Encode the entire dataset
    data = torch.tensor(tokenizer.encode(text), dtype=torch.long)

    # Split into train and validation (90/10 split)
    n = int(0.9 * len(data))
    train_data = data[:n]
    val_data = data[n:]

    print(f"\nTrain set: {len(train_data):,} tokens")
    print(f"Val set: {len(val_data):,} tokens")

    # Create model
    model = RPGItemGPT(tokenizer.vocab_size).to(device)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nModel created with {total_params:,} parameters")

    # Create optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    # Train
    train(model, train_data, val_data, optimizer, max_iters, eval_interval, eval_iters)

    # Save final model
    final_model_path = os.path.join(args.output_dir, 'final_model.pt')
    torch.save({
        'model_state_dict': model.state_dict(),
        'tokenizer_chars': tokenizer.chars,
        'vocab_size': tokenizer.vocab_size,
    }, final_model_path)
    print(f"\nFinal model saved to '{final_model_path}'")

    # Generate some sample items
    generate_sample_items(model, tokenizer, num_items=10)

    print("\n" + "=" * 80)
    print("Training complete! Use generate.py to create new items.")
    print("=" * 80)


if __name__ == '__main__':
    main()
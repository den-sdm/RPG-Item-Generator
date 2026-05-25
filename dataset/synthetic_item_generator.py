import random
import json

# Rarity tiers with stat multipliers
RARITIES = {
    'COMMON': {'color': 'gray', 'stat_count': (1, 2), 'stat_mult': (0.5, 1.0)},
    'UNCOMMON': {'color': 'green', 'stat_count': (2, 3), 'stat_mult': (0.8, 1.5)},
    'RARE': {'color': 'blue', 'stat_count': (3, 4), 'stat_mult': (1.2, 2.0)},
    'EPIC': {'color': 'purple', 'stat_count': (4, 5), 'stat_mult': (1.8, 3.0)},
    'LEGENDARY': {'color': 'orange', 'stat_count': (4, 6), 'stat_mult': (2.5, 4.5)}
}

# Item types with base damage/armor ranges
ITEM_TYPES = {
    'weapon-sword': {'base_dmg': (15, 35), 'stat_pool': ['STR', 'CRIT_CHANCE', 'CRIT_DMG', 'ATTACK_SPEED']},
    'weapon-dagger': {'base_dmg': (10, 25), 'stat_pool': ['DEX', 'CRIT_CHANCE', 'ATTACK_SPEED', 'BLEED_CHANCE']},
    'weapon-axe': {'base_dmg': (20, 40), 'stat_pool': ['STR', 'CRIT_DMG', 'CLEAVE_DMG']},
    'weapon-bow': {'base_dmg': (18, 32), 'stat_pool': ['DEX', 'CRIT_CHANCE', 'PROJECTILE_SPEED', 'PIERCE_CHANCE']},
    'weapon-staff': {'base_dmg': (12, 28), 'stat_pool': ['INT', 'CAST_SPEED', 'SPELL_DMG', 'MANA_REGEN']},
    'weapon-wand': {'base_dmg': (8, 20), 'stat_pool': ['INT', 'CAST_SPEED', 'SPELL_CRIT']},
    'armor-chest': {'base_arm': (50, 120), 'stat_pool': ['STR', 'DEX', 'INT', 'MAX_LIFE', 'ARMOR']},
    'armor-helm': {'base_arm': (30, 80), 'stat_pool': ['STR', 'INT', 'MAX_LIFE', 'MAX_MANA']},
    'armor-gloves': {'base_arm': (20, 60), 'stat_pool': ['DEX', 'ATTACK_SPEED', 'ACCURACY']},
    'armor-boots': {'base_arm': (25, 70), 'stat_pool': ['DEX', 'MOVEMENT_SPEED', 'DODGE_CHANCE']},
    'accessory-ring': {'stat_pool': ['STR', 'DEX', 'INT', 'CRIT_CHANCE', 'LIFE_REGEN', 'RESIST_FIRE', 'RESIST_COLD',
                                     'RESIST_LIGHTNING']},
    'accessory-amulet': {'stat_pool': ['STR', 'DEX', 'INT', 'MAX_LIFE', 'MAX_MANA', 'SPELL_DMG', 'RESIST_ALL']}
}

# Stat ranges and formatting
STAT_RANGES = {
    'STR': (10, 80, '+{} STR'),
    'DEX': (10, 80, '+{} DEX'),
    'INT': (10, 80, '+{} INT'),
    'MAX_LIFE': (30, 150, '+{} Max Life'),
    'MAX_MANA': (20, 100, '+{} Max Mana'),
    'ARMOR': (20, 150, '+{} Armor'),
    'CRIT_CHANCE': (5, 25, '+{}% Crit Chance'),
    'CRIT_DMG': (10, 80, '+{}% Crit Damage'),
    'ATTACK_SPEED': (5, 20, '+{}% Attack Speed'),
    'CAST_SPEED': (8, 25, '+{}% Cast Speed'),
    'MOVEMENT_SPEED': (5, 15, '+{}% Movement Speed'),
    'DODGE_CHANCE': (5, 18, '+{}% Dodge Chance'),
    'BLEED_CHANCE': (10, 30, '+{}% Bleed Chance'),
    'PIERCE_CHANCE': (8, 25, '+{}% Pierce Chance'),
    'SPELL_DMG': (10, 50, '+{}% Spell Damage'),
    'SPELL_CRIT': (8, 20, '+{}% Spell Crit Chance'),
    'CLEAVE_DMG': (15, 40, '+{}% Cleave Damage'),
    'PROJECTILE_SPEED': (10, 30, '+{}% Projectile Speed'),
    'LIFE_REGEN': (5, 25, '+{} Life per Second'),
    'MANA_REGEN': (3, 15, '+{} Mana per Second'),
    'ACCURACY': (50, 200, '+{} Accuracy'),
    'RESIST_FIRE': (10, 40, '+{}% Fire Resistance'),
    'RESIST_COLD': (10, 40, '+{}% Cold Resistance'),
    'RESIST_LIGHTNING': (10, 40, '+{}% Lightning Resistance'),
    'RESIST_ALL': (8, 20, '+{}% All Resistances')
}

# Name components
PREFIXES = [
    'Ancient', 'Cursed', 'Divine', 'Ethereal', 'Flame', 'Frost', 'Shadow', 'Storm',
    'Death', 'Soul', 'Void', 'Dragon', 'Demon', 'Holy', 'Dark', 'Blood',
    'Thunder', 'Arcane', 'Savage', 'Primal', 'Corrupted', 'Blessed', 'Eternal',
    'Phantom', 'Spectral', 'Infernal', 'Celestial', 'Abyssal', 'Radiant', 'Venomous'
]

WEAPON_NAMES = [
    'Blade', 'Edge', 'Reaver', 'Fang', 'Talon', 'Cleaver', 'Slayer', 'Render',
    'Bane', 'Fury', 'Wrath', 'Doom', 'Ender', 'Splitter', 'Piercer', 'Carver',
    'Striker', 'Crusher', 'Sunder', 'Breaker'
]

ARMOR_NAMES = [
    'Guard', 'Ward', 'Plate', 'Aegis', 'Bulwark', 'Carapace', 'Shell', 'Hide',
    'Veil', 'Mantle', 'Embrace', 'Shroud', 'Cuirass', 'Hauberk', 'Harness'
]

ACCESSORY_NAMES = [
    'Band', 'Loop', 'Circle', 'Halo', 'Talisman', 'Charm', 'Relic', 'Sigil',
    'Token', 'Pendant', 'Medallion', 'Locket'
]

# Flavor text templates
FLAVOR_TEMPLATES = {
    'weapon': [
        'Forged in the fires of {}.',
        'The blade whispers {} to its wielder.',
        'Crafted by {} for the ancient wars.',
        'It hungers for {}.',
        'Once wielded by {}.',
        'Imbued with the essence of {}.',
        'Every strike echoes with {}.',
        'Born from {}.',
        'A weapon of {} and destruction.',
        'Tempered in {}.'
    ],
    'armor': [
        'Worn by {} in ages past.',
        'Provides protection against {}.',
        'Woven with threads of {}.',
        'Blessed by {} for the faithful.',
        'Forged to withstand {}.',
        'Grants the wearer {}.',
        'Said to have protected {} from certain death.',
        'Infused with {}.',
        'A relic from the age of {}.',
        'Bears the mark of {}.'
    ],
    'accessory': [
        'Contains a fragment of {}.',
        'Grants visions of {}.',
        'Pulses with {}.',
        'A gift from {}.',
        'Channels the power of {}.',
        'Whispers secrets of {}.',
        'Bound to {} by ancient magic.',
        'Resonates with {}.',
        'Holds the essence of {}.',
        'Attracts {}.'
    ]
}

FLAVOR_FILLERS = [
    'the void', 'ancient dragons', 'forgotten gods', 'the abyss', 'eternal flames',
    'chaos', 'shadow magic', 'the underworld', 'celestial beings', 'dark rituals',
    'blood and fury', 'the storm', 'demonic forces', 'holy light', 'the elements',
    'war and glory', 'forbidden knowledge', 'lost souls', 'primordial power', 'death itself',
    'legendary warriors', 'divine champions', 'cursed kings', 'elder wizards', 'fallen heroes',
    'mythical beasts', 'cosmic energy', 'arcane mysteries', 'destructive power', 'the depths'
]


def generate_item_name(item_type):
    """Generate a fantasy item name."""
    prefix = random.choice(PREFIXES)

    if 'weapon' in item_type:
        suffix = random.choice(WEAPON_NAMES)
    elif 'armor' in item_type:
        suffix = random.choice(ARMOR_NAMES)
    else:  # accessory
        suffix = random.choice(ACCESSORY_NAMES)

    # Sometimes add "of X" suffix
    if random.random() < 0.3:
        of_suffix = random.choice(['the Void', 'Dragons', 'Shadows', 'the Storm', 'Eternity', 'the Damned'])
        return f"{prefix} {suffix} of {of_suffix}"

    return f"{prefix} {suffix}"


def generate_stats(item_type, rarity):
    """Generate stats for an item based on type and rarity."""
    config = ITEM_TYPES[item_type]
    rarity_config = RARITIES[rarity]

    stats = []

    # Add damage or armor
    if 'base_dmg' in config:
        min_dmg, max_dmg = config['base_dmg']
        mult_min, mult_max = rarity_config['stat_mult']
        scaled_min = int(min_dmg * random.uniform(mult_min, mult_max))
        scaled_max = int(max_dmg * random.uniform(mult_min, mult_max))
        stats.append(f"DMG: {scaled_min}-{scaled_max}")
    elif 'base_arm' in config:
        min_arm, max_arm = config['base_arm']
        mult_min, mult_max = rarity_config['stat_mult']
        scaled_arm = int(random.uniform(min_arm, max_arm) * random.uniform(mult_min, mult_max))
        stats.append(f"ARM: {scaled_arm}")

    # Add random stats from pool
    stat_count = random.randint(*rarity_config['stat_count'])
    available_stats = config['stat_pool'].copy()

    for _ in range(min(stat_count, len(available_stats))):
        stat_key = random.choice(available_stats)
        available_stats.remove(stat_key)

        min_val, max_val, fmt = STAT_RANGES[stat_key]
        mult_min, mult_max = rarity_config['stat_mult']
        value = int(random.uniform(min_val, max_val) * random.uniform(mult_min, mult_max))
        stats.append(fmt.format(value))

    return stats


def generate_flavor_text(item_type):
    """Generate flavor text for an item."""
    category = 'weapon' if 'weapon' in item_type else ('armor' if 'armor' in item_type else 'accessory')
    template = random.choice(FLAVOR_TEMPLATES[category])
    filler = random.choice(FLAVOR_FILLERS)
    return template.format(filler)


def generate_item():
    """Generate a complete RPG item."""
    rarity = random.choices(
        list(RARITIES.keys()),
        weights=[50, 30, 15, 4, 1]  # Common is most frequent
    )[0]

    item_type = random.choice(list(ITEM_TYPES.keys()))
    name = generate_item_name(item_type)
    stats = generate_stats(item_type, rarity)
    flavor = generate_flavor_text(item_type)

    # Format: [RARITY] Name | Type | Stat1 | Stat2 | ... | "Flavor"
    stats_str = ' | '.join(stats)
    item_str = f'[{rarity}] {name} | {item_type} | {stats_str} | "{flavor}"'

    return {
        'text': item_str,
        'rarity': rarity,
        'name': name,
        'type': item_type,
        'stats': stats,
        'flavor': flavor
    }


def generate_dataset(num_items, output_file='synthetic_items.txt', json_file='synthetic_items.json'):
    """Generate a dataset of synthetic items."""
    print(f"Generating {num_items} synthetic items...")

    items = []
    items_text = []

    for i in range(num_items):
        if (i + 1) % 1000 == 0:
            print(f"Generated {i + 1}/{num_items} items...")

        item = generate_item()
        items.append(item)
        items_text.append(item['text'])

    # Save as text file (for training)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(items_text))

    # Save as JSON (for analysis/visualization)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"\nDataset saved to:")
    print(f"  - {output_file} ({len(items_text)} items)")
    print(f"  - {json_file} (structured data)")

    # Print statistics
    rarity_counts = {}
    type_counts = {}
    for item in items:
        rarity_counts[item['rarity']] = rarity_counts.get(item['rarity'], 0) + 1
        type_counts[item['type']] = type_counts.get(item['type'], 0) + 1

    print("\nRarity distribution:")
    for rarity in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY']:
        count = rarity_counts.get(rarity, 0)
        pct = (count / num_items) * 100
        print(f"  {rarity}: {count} ({pct:.1f}%)")

    print("\nType distribution:")
    for item_type, count in sorted(type_counts.items()):
        pct = (count / num_items) * 100
        print(f"  {item_type}: {count} ({pct:.1f}%)")

    # Show 5 example items
    print("\nExample items:")
    for i, item in enumerate(random.sample(items, min(5, len(items))), 1):
        print(f"\n{i}. {item['text']}")


if __name__ == '__main__':
    # Generate 10,000 synthetic items
    generate_dataset(10000)
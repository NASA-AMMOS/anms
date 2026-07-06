#!/usr/bin/env python3
"""DB Pool Optimization Patch for ANMS.

Applies optimized connection pool settings to config.py and validates they fit
within PostgreSQL's max_connections limit.

Usage:
    # Dry run - show what would change
    python3 scripts/db_pool_optimizer.py --dry-run

    # Apply patch
    python3 scripts/db_pool_optimizer.py --apply

    # Revert to original
    python3 scripts/db_pool_optimizer.py --revert

    # Just show current config
    python3 scripts/db_pool_optimizer.py --status
"""

import argparse
import re
import sys
from pathlib import Path

# Recommended pool settings
OPTIMIZED_CONFIG = {
    'DB_POOL_SIZE': 20,       # 4 workers × 20 = 80 base connections
    'DB_MAX_OVERFLOW': 10,    # 90 total (fits under PG 100)
    'DB_POOL_TIMEOUT': 5,     # Fail fast instead of 30s
    'DB_POOL_RECYCLE': 1800,  # 30 min instead of 1 hour
}

# Current defaults in config.py
CURRENT_CONFIG = {
    'DB_POOL_SIZE': 50,
    'DB_MAX_OVERFLOW': 10,
    'DB_POOL_TIMEOUT': 30,
    'DB_POOL_RECYCLE': 3600,
}

CONFIG_FILE = Path(__file__).parent.parent / 'anms-core' / 'anms' / 'shared' / 'config.py'


def read_config():
    """Read current DB pool config from config.py."""
    content = CONFIG_FILE.read_text()
    config = {}
    for key in ['DB_POOL_SIZE', 'DB_MAX_OVERFLOW', 'DB_POOL_TIMEOUT', 'DB_POOL_RECYCLE']:
        match = re.search(rf'{key}\s*=\s*(\d+)', content)
        if match:
            config[key] = int(match.group(1))
    return config


def get_server_workers():
    """Read SERVER_WORKERS from config.py."""
    cfg_file = Path(__file__).parent.parent / 'anms-core' / 'anms' / 'shared' / 'config.py'
    content = cfg_file.read_text()
    match = re.search(r'SERVER_WORKERS\s*=\s*(\d+)', content)
    return int(match.group(1)) if match else 4


def calculate_pool_usage(config, workers=None):
    """Calculate total DB connections with current config."""
    if workers is None:
        workers = get_server_workers()
    base = config['DB_POOL_SIZE'] * workers
    overflow = config['DB_MAX_OVERFLOW'] * workers
    return {
        'base_connections': base,
        'max_overflow': overflow,
        'total_max': base + overflow,
        'fits_in_pg_default': (base + overflow) <= 100,
        'workers': workers,
    }


def show_status():
    """Show current DB pool configuration."""
    current = read_config()
    usage = calculate_pool_usage(current)
    
    print("\n" + "="*70)
    print("DB POOL CONFIGURATION STATUS")
    print("="*70)
    print(f"\nCurrent settings (config.py):")
    print(f"  DB_POOL_SIZE:    {current.get('DB_POOL_SIZE', 'N/A')}")
    print(f"  DB_MAX_OVERFLOW: {current.get('DB_MAX_OVERFLOW', 'N/A')}")
    print(f"  DB_POOL_TIMEOUT: {current.get('DB_POOL_TIMEOUT', 'N/A')}")
    print(f"  DB_POOL_RECYCLE: {current.get('DB_POOL_RECYCLE', 'N/A')}")
    
    print(f"\nConnection usage ({usage['workers']} workers):")
    print(f"  Base connections:  {usage['base_connections']}")
    print(f"  Max overflow:      {usage['max_overflow']}")
    print(f"  Total max:         {usage['total_max']}")
    print(f"  Fits in PG default (100): {'✓ YES' if usage['fits_in_pg_default'] else '✗ NO - WILL CAUSE POOL EXHAUSTION'}")
    
    optimized_usage = calculate_pool_usage(OPTIMIZED_CONFIG)
    print(f"\nRecommended settings:")
    print(f"  DB_POOL_SIZE:    {OPTIMIZED_CONFIG['DB_POOL_SIZE']}")
    print(f"  DB_MAX_OVERFLOW: {OPTIMIZED_CONFIG['DB_MAX_OVERFLOW']}")
    print(f"  DB_POOL_TIMEOUT: {OPTIMIZED_CONFIG['DB_POOL_TIMEOUT']}")
    print(f"  DB_POOL_RECYCLE: {OPTIMIZED_CONFIG['DB_POOL_RECYCLE']}")
    print(f"  Total max connections: {optimized_usage['total_max']}")
    
    print()


def dry_run():
    """Show what changes would be made."""
    current = read_config()
    
    print("\n" + "="*70)
    print("DB POOL OPTIMIZATION - DRY RUN")
    print("="*70)
    
    for key, new_val in OPTIMIZED_CONFIG.items():
        old_val = current.get(key, 'N/A')
        status = "→ CHANGE" if old_val != new_val else "→ OK"
        print(f"  {key:20} {old_val} → {new_val} {status}")
    print()


def apply_patch():
    """Apply optimized DB pool settings."""
    content = CONFIG_FILE.read_text()
    
    for key, value in OPTIMIZED_CONFIG.items():
        pattern = rf'({key}\s*=\s*)\d+'
        replacement = rf'\g<1>{value}'
        content = re.sub(pattern, replacement, content)
    
    CONFIG_FILE.write_text(content)
    print("✓ DB pool settings updated in config.py")
    show_status()


def revert_patch():
    """Revert to original DB pool settings."""
    content = CONFIG_FILE.read_text()
    
    for key, value in CURRENT_CONFIG.items():
        pattern = rf'({key}\s*=\s*)\d+'
        replacement = rf'\g<1>{value}'
        content = re.sub(pattern, replacement, content)
    
    CONFIG_FILE.write_text(content)
    print("✓ Reverted to original DB pool settings")
    show_status()


def main():
    parser = argparse.ArgumentParser(description='DB Pool Optimization Patch')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--apply', action='store_true', help='Apply optimized settings')
    parser.add_argument('--revert', action='store_true', help='Revert to original settings')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    args = parser.parse_args()
    
    if args.dry_run:
        dry_run()
    elif args.apply:
        apply_patch()
    elif args.revert:
        revert_patch()
    else:
        show_status()


if __name__ == '__main__':
    main()

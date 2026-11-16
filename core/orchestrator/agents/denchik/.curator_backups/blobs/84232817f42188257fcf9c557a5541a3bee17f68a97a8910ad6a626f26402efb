#!/usr/bin/env python3
"""
Validates that all t:... translation keys referenced across Shopify theme
configuration and sections exist in locales schema / translation dictionaries.
"""
import os
import re
import json
import sys

def get_nested(dic, key_path):
    curr = dic
    for part in key_path.split('.'):
        if not isinstance(curr, dict) or part not in curr:
            return None
        curr = curr[part]
    return curr

def load_json_clean(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    # Strip C-style comments: /* ... */
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    try:
        return json.loads(text)
    except Exception as e:
        print(f"Warning: Failed to parse {path}: {e}")
        return {}

def validate_theme_translations(theme_dir: str, locale: str = 'en.default') -> bool:
    schema_path = os.path.join(theme_dir, 'locales', f'{locale}.schema.json')
    default_trans_path = os.path.join(theme_dir, 'locales', f'{locale}.json')

    if not os.path.exists(schema_path):
        print(f"Error: {schema_path} does not exist.")
        return False

    schema_dict = load_json_clean(schema_path)
    trans_dict = load_json_clean(default_trans_path)

    # 1. Collect all t: keys from config/settings_schema.json
    all_keys = set()
    cfg_path = os.path.join(theme_dir, 'config', 'settings_schema.json')
    if os.path.exists(cfg_path):
        with open(cfg_path, 'r', encoding='utf-8', errors='ignore') as f:
            cfg_content = f.read()
            for m in re.finditer(r'"t:([^"]+)"', cfg_content):
                all_keys.add(m.group(1))

    # 2. Collect all t: keys from sections/*.liquid, blocks/*.liquid, snippets/*.liquid
    for folder in ['sections', 'blocks', 'snippets']:
        scan_dir = os.path.join(theme_dir, folder)
        if os.path.exists(scan_dir):
            for f in os.listdir(scan_dir):
                if f.endswith('.liquid'):
                    p = os.path.join(scan_dir, f)
                    with open(p, 'r', encoding='utf-8', errors='ignore') as sfile:
                        content = sfile.read()
                        for m in re.finditer(r'"t:([^"]+)"', content):
                            all_keys.add(m.group(1))

    # 3. Check presence
    missing = []
    for k in sorted(all_keys):
        in_schema = get_nested(schema_dict, k) is not None
        in_trans = get_nested(trans_dict, k) is not None
        if not (in_schema or in_trans):
            missing.append(k)

    if missing:
        print(f"FAILED: Found {len(missing)} missing translation key(s):")
        for k in missing:
            print(f"  - t:{k}")
        return False

    print(f"SUCCESS: All {len(all_keys)} translation keys verified in {theme_dir}.")
    return True

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'services/dnk_shopify/DNK-e.com'
    success = validate_theme_translations(target)
    sys.exit(0 if success else 1)

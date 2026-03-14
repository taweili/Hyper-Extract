#!/usr/bin/env python3
"""YAML Configuration Migration Script.

Migrates YAML configuration files from old format to new format.

Usage:
    python scripts/migrate_yaml_configs.py
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Union


def convert_rules_to_array(rules_value: Union[str, List[str], Dict[str, Union[str, List[str]]]]) -> Union[List[str], Dict[str, List[str]]]:
    """Convert string format rules to array format."""
    if rules_value is None:
        return None
    
    if isinstance(rules_value, list):
        return rules_value
    
    if isinstance(rules_value, dict):
        result = {}
        for lang, value in rules_value.items():
            if isinstance(value, str):
                lines = []
                for line in value.strip().split('\n'):
                    line = line.strip()
                    if line and line[0].isdigit():
                        parts = line.split('.', 1)
                        if len(parts) > 1:
                            line = parts[1].strip()
                        else:
                            line = ''.join(c for c in line if not c.isdigit() and c not in '.、').strip()
                    if line:
                        lines.append(line)
                result[lang] = lines
            else:
                result[lang] = value
        return result
    
    if isinstance(rules_value, str):
        lines = []
        for line in rules_value.strip().split('\n'):
            line = line.strip()
            if line and line[0].isdigit():
                parts = line.split('.', 1)
                if len(parts) > 1:
                    line = parts[1].strip()
                else:
                    line = ''.join(c for c in line if not c.isdigit() and c not in '.、').strip()
            if line:
                lines.append(line)
        return lines
    
    return rules_value


def migrate_yaml_config(old: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate single YAML configuration."""
    new = {}
    
    new["language"] = old.get("language", "zh")
    new["name"] = old["name"]
    new["type"] = old.get("autotype", "model")
    new["tags"] = old.get("tag", [])
    new["description"] = old.get("description", {})
    
    autotype = new["type"]
    
    if autotype in ("model", "list", "set"):
        old_schema = old.get("schema") or old.get("item_schema", {})
        new["output"] = {
            "description": old_schema.get("description", {}),
            "fields": old_schema.get("fields", [])
        }
    else:
        old_node_schema = old.get("node_schema", {})
        old_edge_schema = old.get("edge_schema", {})
        
        new["output"] = {
            "description": {},
            "entities": {
                "description": old_node_schema.get("description", {}),
                "fields": old_node_schema.get("fields", [])
            },
            "relations": {
                "description": old_edge_schema.get("description", {}),
                "fields": old_edge_schema.get("fields", [])
            }
        }
    
    if "guide" in old:
        guide = old["guide"]
        new_guideline = {}
        
        if "target" in guide:
            new_guideline["target"] = guide["target"]
        
        rules_fields = ["rules", "rules_for_nodes", "rules_for_edges", "rules_for_time", "rules_for_location"]
        new_rules_fields = ["rules", "rules_for_entities", "rules_for_relations", "rules_for_time", "rules_for_location"]
        
        for old_field, new_field in zip(rules_fields, new_rules_fields):
            if old_field in guide:
                new_guideline[new_field] = convert_rules_to_array(guide[old_field])
        
        if new_guideline:
            new["guideline"] = new_guideline
    
    if "identifiers" in old:
        ids = old["identifiers"]
        if ids is None:
            ids = {}
        new_ids = {}
        if "item_id" in ids:
            new_ids["item_id"] = ids["item_id"]
        if "node_id" in ids:
            new_ids["entity_id"] = ids["node_id"]
        if "edge_id" in ids:
            new_ids["relation_id"] = ids["edge_id"]
        if "edge_members" in ids:
            new_ids["relation_members"] = ids["edge_members"]
        if "time_field" in ids:
            new_ids["time_field"] = ids["time_field"]
        if "location_field" in ids:
            new_ids["location_field"] = ids["location_field"]
        if new_ids:
            new["identifiers"] = new_ids
    
    if "options" in old:
        opts = old["options"]
        new_opts = {}
        for key in ["merge_strategy", "extraction_mode", "chunk_size", "chunk_overlap", "max_workers", "verbose"]:
            if key in opts:
                new_opts[key] = opts[key]
        if "node_merge_strategy" in opts:
            new_opts["entity_merge_strategy"] = opts["node_merge_strategy"]
        if "edge_merge_strategy" in opts:
            new_opts["relation_merge_strategy"] = opts["edge_merge_strategy"]
        if "search_fields" in opts:
            new_opts["fields_for_search"] = opts["search_fields"]
        if "node_search_fields" in opts:
            new_opts["entity_fields_for_search"] = opts["node_search_fields"]
        if "edge_search_fields" in opts:
            new_opts["relation_fields_for_search"] = opts["edge_search_fields"]
        if new_opts:
            new["options"] = new_opts
    
    if "display" in old:
        disp = old["display"]
        new_disp = {}
        if "label" in disp:
            new_disp["label"] = disp["label"]
        if "node_label" in disp:
            new_disp["entity_label"] = disp["node_label"]
        if "edge_label" in disp:
            new_disp["relation_label"] = disp["edge_label"]
        if new_disp:
            new["display"] = new_disp
    
    return new


def migrate_all_yaml_files(presets_dir: Path, dry_run: bool = False):
    """Migrate all YAML files."""
    yaml_files = list(presets_dir.rglob("*.yaml"))
    print(f"Found {len(yaml_files)} YAML files to migrate")
    
    for yaml_file in yaml_files:
        print(f"\nProcessing: {yaml_file}")
        
        with open(yaml_file, "r", encoding="utf-8") as f:
            old_config = yaml.safe_load(f)
        
        if old_config is None:
            print(f"  Skipping empty file")
            continue
        
        if "autotype" not in old_config and "type" in old_config:
            print(f"  Already migrated, skipping")
            continue
        
        new_config = migrate_yaml_config(old_config)
        
        if dry_run:
            print(f"  [DRY RUN] Would write new config:")
            print(yaml.dump(new_config, allow_unicode=True, default_flow_style=False, sort_keys=False)[:500])
        else:
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(new_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"  Migrated successfully")
    
    print(f"\nMigration complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate YAML configuration files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--path", type=str, default=None, help="Path to presets directory")
    args = parser.parse_args()
    
    if args.path:
        presets_dir = Path(args.path)
    else:
        presets_dir = Path(__file__).parent.parent / "hyperextract" / "templates" / "presets"
    
    print(f"Presets directory: {presets_dir}")
    migrate_all_yaml_files(presets_dir, dry_run=args.dry_run)

"""
Run Template - 执行预设模板测试

Usage:
    python examples/templates/run_template.py -d <domain> -t <template_name>

    or edit CONFIG below to set default domain and template

Examples:
    python examples/templates/run_template.py -d finance -t earnings_summary
    python examples/templates/run_template.py -d general -t base_graph
    python examples/templates/run_template.py -d tcm -t formula_composition
"""

import argparse
import sys
import yaml
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

CONFIG = {
    "domain": "general",
    "template": "base_graph",
}


def load_mappings():
    mapping_file = Path(__file__).parent / "templates_mapping.yaml"
    with open(mapping_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_template(domain: str, template_name: str):
    mappings = load_mappings()

    if domain not in mappings:
        print(f"Error: Domain '{domain}' not found.")
        print(f"Available domains: {', '.join(mappings.keys())}")
        return False

    domain_mappings = mappings[domain]

    if template_name not in domain_mappings:
        print(f"Error: Template '{template_name}' not found in domain '{domain}'.")
        print("Available templates:")
        for name in domain_mappings.keys():
            print(f"  - {name}")
        return False

    template_info = domain_mappings[template_name]
    template_path = project_root / "hyperextract" / "templates" / "presets" / f"{template_info['template']}.yaml"
    input_path = project_root / "tests" / "test_data" / "zh" / template_info["input"]

    print("\n" + "=" * 80)
    print(f"🧪 Template Test: {domain}/{template_name}")
    print("=" * 80)

    print(f"\n📄 Template: {template_path}")
    print(f"📥 Input: {input_path}")

    if not template_path.exists():
        print(f"\n❌ Error: Template file not found: {template_path}")
        return False

    if not input_path.exists():
        print(f"\n❌ Error: Input file not found: {input_path}")
        return False

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    with open(input_path, "r", encoding="utf-8") as f:
        input_content = f.read()

    print("\n" + "-" * 80)
    print("📋 Template Content:")
    print("-" * 80)
    print(template_content[:500] + "..." if len(template_content) > 500 else template_content)

    print("\n" + "-" * 80)
    print(f"📖 Input Content ({len(input_content)} chars):")
    print("-" * 80)
    print(input_content[:500] + "..." if len(input_content) > 500 else input_content)

    print("\n" + "-" * 80)
    print("⚙️  Running extraction...")
    print("-" * 80)

    print("\n✅ Template and input loaded successfully!")
    print("\n   To implement full extraction, integrate with:")
    print("   - AutoGraph for graph extraction")
    print("   - AutoHypergraph for hypergraph extraction")
    print("   - AutoList for list extraction")
    print("   - AutoModel for model extraction")
    print("   - AutoSet for set extraction")
    print("   - AutoTemporalGraph for temporal graph extraction")
    print("   - AutoSpatialGraph for spatial graph extraction")
    print("   - AutoSpatioTemporalGraph for spatio-temporal graph extraction")

    print("\n" + "=" * 80 + "\n")

    return True


def main():
    parser = argparse.ArgumentParser(description="Run Hyper-Extract preset template test")
    parser.add_argument("-d", "--domain", help="Domain name (e.g., finance, general, tcm)")
    parser.add_argument("-t", "--template", help="Template name (e.g., earnings_summary, base_graph)")

    args = parser.parse_args()

    domain = args.domain if args.domain else CONFIG["domain"]
    template = args.template if args.template else CONFIG["template"]

    if not args.domain and not args.template:
        print("\n📝 Using default config from file:")
        print(f"   Domain: {domain}")
        print(f"   Template: {template}")
        print("   (Use -d and -t to override)\n")

    success = run_template(domain, template)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

import os
import json
import re

def parse_langfuse_prompt(content):
    if not content.startswith("Chat prompt"):
        return None
    
    lines = content.splitlines()
    
    sections = {}
    current_section = None
    section_content = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line == "system":
            current_section = "system"
            section_content = []
            i += 1
            continue
        elif line == "user":
            if current_section:
                sections[current_section] = "\n".join(section_content).strip()
            current_section = "user"
            section_content = []
            i += 1
            continue
        elif line == "Variables":
            if current_section:
                sections[current_section] = "\n".join(section_content).strip()
            current_section = "variables"
            section_content = []
            i += 1
            continue
        elif line == "Config":
            if current_section:
                sections[current_section] = "\n".join(section_content).strip()
            current_section = "config"
            section_content = []
            i += 1
            continue
            
        section_content.append(lines[i])
        i += 1
        
    if current_section and section_content:
        sections[current_section] = "\n".join(section_content).strip()
        
    # Process system and user content to remove wrapping quotes if they exist
    for key in ["system", "user"]:
        if key in sections:
            text = sections[key]
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1].strip()
            sections[key] = text
            
    # Process config
    if "config" in sections:
        config_text = sections["config"]
        # Convert non-strict JSON to dict
        # Simple regex to quote keys
        config_text = re.sub(r'(\w+):', r'"\1":', config_text)
        try:
            sections["config"] = json.loads(config_text)
        except json.JSONDecodeError:
            # Fallback if complex
            sections["config"] = config_text
            
    return {
        "system": sections.get("system", ""),
        "user": sections.get("user", ""),
        "config": sections.get("config", {})
    }

def main():
    prompts_dir = r"c:\Users\marav\OneDrive\Документы\podpolie\repos\politicalNLP2026\prompts"
    for filename in os.listdir(prompts_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(prompts_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            parsed = parse_langfuse_prompt(content)
            if parsed:
                json_filename = filename.replace(".txt", ".json")
                json_filepath = os.path.join(prompts_dir, json_filename)
                with open(json_filepath, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)
                print(f"Converted {filename} to {json_filename}")
            else:
                print(f"Skipped {filename} (not a Langfuse copy)")

if __name__ == "__main__":
    main()

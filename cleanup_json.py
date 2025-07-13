import json
import re

def clean_description(text):
    """Clean up the checklist_ai_description text by removing markdown and formatting properly"""
    
    # Remove ** bold markers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # Replace \\n with actual line breaks
    text = text.replace('\\n', '\n')
    
    # Clean up numbered lists - convert to 1), 2), etc format
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Convert numbered lists from "1. **text**" to "1) text"
        line = re.sub(r'^(\d+)\.\s*\*\*(.*?)\*\*\s*(.*)', r'\1) \2 \3', line)
        # Convert simple numbered lists from "1. text" to "1) text"  
        line = re.sub(r'^(\d+)\.\s*', r'\1) ', line)
        
        # Clean up bullet points - convert • to -
        line = line.replace('•', '-')
        
        cleaned_lines.append(line)
    
    # Join lines back together
    text = '\n'.join(cleaned_lines)
    
    # Remove multiple consecutive line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def main():
    # Read the original JSON file
    with open('final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Clean up each checklist item
    for item in data:
        if 'checklist_ai_description' in item:
            item['checklist_ai_description'] = clean_description(item['checklist_ai_description'])
    
    # Write the cleaned JSON file
    with open('final_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Cleaned JSON file saved as 'final_cleaned.json'")
    print("Sample cleaned description:")
    print("="*50)
    print(data[0]['checklist_ai_description'][:500] + "...")

if __name__ == "__main__":
    main() 
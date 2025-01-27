import json
import re
import sys

def convert_chat_text_to_prompt_completion(input_file, output_file):
    """
    Reads a JSONL file where each line is in the form:
    {
        "text": "<|im_start|>user\\nUser message<|im_end|>\\n<|im_start|>assistant\\nAssistant message<|im_end|>"
    }
    and outputs a JSONL file where each line is in the format:
    {
        "prompt": "User message",
        "completion": "Assistant message"
    }
    """

    # Regex patterns to capture user and assistant content
    user_pattern = re.compile(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', re.DOTALL)
    assistant_pattern = re.compile(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', re.DOTALL)

    with open(input_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue  # Skip any empty lines

            data = json.loads(line)
            text = data.get("text", "")

            # Extract user and assistant messages
            user_match = user_pattern.search(text)
            assistant_match = assistant_pattern.search(text)

            user_content = user_match.group(1).strip() if user_match else ""
            assistant_content = assistant_match.group(1).strip() if assistant_match else ""

            # Construct the new record
            new_data = {
                "prompt": user_content,
                "completion": assistant_content
            }

            # Write to output file as JSONL
            json.dump(new_data, fout, ensure_ascii=False)
            fout.write('\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_chat_text_to_prompt_completion.py <input_file.jsonl> <output_file.jsonl>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_chat_text_to_prompt_completion(input_file, output_file)
    print(f"Conversion complete. Output written to {output_file}")

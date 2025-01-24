import random
import json

# 1) Define sets of words/phrases for placeholders
TOPICS = ["life", "happiness", "love", "time", "the universe", "personal finance", "dieting"]
OBJECTS = ["laptop", "phone", "car", "bicycle", "printer", "coffee machine"]
CONCEPTS = ["photosynthesis", "quantum mechanics", "the stock market", "geopolitics", "machine learning"]
GENRES = ["mystery novel", "fantasy novel", "self-help book", "biography", "historical fiction"]

# 2) Define user message templates
# Each template contains placeholders like {topic}, {object}, etc.
USER_TEMPLATES = [
    "What is the meaning of {topic}?",
    "Where can I find good info on {topic}?",
    "Tell me how to fix a {object}.",
    "Explain {concept} in simple terms.",
    "Recommend me a {genre} to read.",
    "Can you share a random fact about {topic}?",
    "How do I troubleshoot a {object}?",
    "I’d like to learn more about {concept}.",
    "Do you have any tips for understanding {concept}?",
    "What’s the best way to choose a {genre}?",
]

# 3) Define assistant message templates
# These can also have placeholders, or just be random statements.
ASSISTANT_TEMPLATES = [
    "Certainly! Here’s a quick overview of {concept}.",
    "Sure. When dealing with {object}, you should first check the manual.",
    "I’m happy to help you explore {topic}.",
    "Many people find that reading a good {genre} can be relaxing.",
    "Let me think about that. I’d suggest starting with the basics of {concept}.",
    "Great question! A {genre} is often recommended by critics if you like character-driven plots.",
    "When it comes to {object}, regular maintenance is key.",
    "A big part of understanding {concept} is looking at foundational principles.",
    "Some experts believe that reflecting on {topic} improves well-being.",
    "Reading about {topic} can open up new perspectives on life."
]

def random_message(template):
    """
    Fills placeholders in a template with random choices
    from the relevant lists.
    """
    msg = template

    # Replace placeholders for each type
    # We check if placeholders exist in the template, then replace them.
    if "{topic}" in msg:
        msg = msg.replace("{topic}", random.choice(TOPICS), 1)
    if "{object}" in msg:
        msg = msg.replace("{object}", random.choice(OBJECTS), 1)
    if "{concept}" in msg:
        msg = msg.replace("{concept}", random.choice(CONCEPTS), 1)
    if "{genre}" in msg:
        msg = msg.replace("{genre}", random.choice(GENRES), 1)

    return msg

def generate_synthetic_chat(num_examples=200):
    """
    Generates synthetic JSON lines with <|im_start|>/ <|im_end|> tokens
    by combining templates and placeholders for user and assistant.
    """

    for _ in range(num_examples):
        # Randomly choose a user template and fill in placeholders
        user_template = random.choice(USER_TEMPLATES)
        user_text = random_message(user_template)

        # Randomly choose an assistant template and fill in placeholders
        assistant_template = random.choice(ASSISTANT_TEMPLATES)
        assistant_text = random_message(assistant_template)

        # Build the synthetic text block with role markers
        text_block = (
            f"<|im_start|>user\n"
            f"{user_text}<|im_end|>\n"
            f"<|im_start|>assistant\n"
            f"{assistant_text}<|im_end|>"
        )

        yield {"text": text_block}

def write_to_jsonl(filename, data_generator):
    with open(filename, "w", encoding="utf-8") as f:
        for record in data_generator:
            f.write(json.dumps(record) + "\n")

if __name__ == "__main__":
    synthetic_data = generate_synthetic_chat(num_examples=200)
    write_to_jsonl("synthetic_dataset.jsonl", synthetic_data)
    print("Synthetic JSONL file created: synthetic_dataset.jsonl")

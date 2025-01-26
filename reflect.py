from ollama import chat

def ask_ollama(question, model="granite3.1-dense"):
    """
    Sends a question prompt to the Ollama model using the ollama library
    and returns the full response text.
    """
    try:
        # Use the chat function from the ollama library to send the prompt
        response = chat(model=model, messages=[
            {
                "role": "user",
                "content": question
            }
        ])

        # Extract and return the content of the response
        return response.message.content

    except Exception as e:
        # Handle any errors raised by the ollama library
        raise SystemExit(f"Error communicating with Ollama API: {e}")


def calculate_and_reflect(question, reasoning):
    """
    Sends an arithmetic challenge to the Ollama API and requests
    step-by-step reasoning plus a reflection on the reasoning process.
    """
    # Construct the prompt for Ollama
    # - <|im_start|> / <|im_end|> tags are used to emulate a conversation style.
    # - We explicitly request a reflection in the <think> tags.
    # - We ask for a final numeric result in the <answer> tags.
    prompt = f"""
<|im_start|>user
Double check the think tags for any mistakes for the following question: "{question}".   
Rewrite the question, and recalculate each reasoning step comparing the step calculations with the original calculation.  Any differences should be pointed out.  This process should be repeated, checking subsequent cycles until a correct answer is achieved.
Original reasoning: {reasoning}
<|im_end|>
<|im_start|>assistant
"""

    try:
        # Make the request to the Ollama API
        response = ask_ollama(prompt)

        # Print the full response (reasoning, reflection, and final answer)
        print("Response from Ollama:")
        print(response)

    except Exception as e:
        print(f"Error communicating with Ollama API: {e}")


# Example usage
if __name__ == "__main__":
    # Expression to solve and reflect upon
    expression = "What’s 5 multiplied by 2?"
    reasoning = "<think>5 multiplied by 2 is very simple arithmetic, I don’t need to break this down.</think>"
    calculate_and_reflect(expression, reasoning)

#!/usr/bin/env python3
import argparse
from verifiers.poetry.haiku_verifier import HaikuVerifier

def main():
    parser = argparse.ArgumentParser(description="Check if a text is a Haiku.")
    parser.add_argument("file", type=str, help="Path to the text file containing the poem.")
    parser.add_argument("--tolerance", type=int, default=1,
                        help="Allowed +/- deviation from the 5-7-5 syllable structure.")
    args = parser.parse_args()

    # Read the file
    with open(args.file, "r", encoding="utf-8") as f:
        poem_text = f.read()

    # Initialize the verifier
    verifier = HaikuVerifier()

    # Get detailed feedback (score + messages)
    result = verifier.verify_with_feedback(poem_text, tolerance=args.tolerance)

    # Print results
    print(f"Score: {result['score']:.2f}")
    print("Feedback:")
    for msg in result["feedback"]:
        print(" -", msg)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import sys

from registry_loader import load_registry, load_verifier_class, add_verifier_arguments

def main():
    base_parser = argparse.ArgumentParser(
        description="Check poems with dynamically loaded verifiers & CLI arguments from JSON."
    )
    base_parser.add_argument("file", type=str, help="Path to the text file containing the poem.")
    base_parser.add_argument("--registry", type=str, default="verifier_registry.json",
                             help="Path to the JSON registry of verifiers.")
    base_parser.add_argument("--verifier", type=str, required=True,
                             help="Which verifier to use (must match registry).")
    base_parser.add_argument("--feedback", action="store_true",
                             help="Use verify_with_feedback if set.")
    
    # We do a first parse just to get --verifier and --registry
    # Then we'll load the registry and parse the chosen verifier's arguments
    partial_args, _ = base_parser.parse_known_args()

    # 1) Load the registry
    registry_data = load_registry(partial_args.registry)

    # 2) Is the chosen verifier known?
    if partial_args.verifier not in registry_data:
        print(f"Unknown verifier '{partial_args.verifier}'. Available options:")
        for name, info in registry_data.items():
            desc = info.get("description", "")
            print(f" - {name}: {desc}")
        sys.exit(1)

    verifier_info = registry_data[partial_args.verifier]

    # 3) We'll create a new parser that includes the dynamic arguments
    #    from the chosen verifier
    parser = argparse.ArgumentParser(
        description=f"Verifier: {partial_args.verifier}. {verifier_info.get('description','')}"
    )
    parser.add_argument("file", type=str, help="Path to the text file containing the poem.")
    parser.add_argument("--registry", type=str, default="verifier_registry.json",
                        help="Path to the JSON registry of verifiers.")
    parser.add_argument("--verifier", type=str, required=True,
                        help="Which verifier to use (must match registry).")
    parser.add_argument("--feedback", action="store_true",
                        help="Use verify_with_feedback if set.")

    # 4) Dynamically add arguments from the JSON
    add_verifier_arguments(parser, verifier_info)

    # Now parse all arguments
    args = parser.parse_args()

    # 5) Load & instantiate the verifier class
    verifier_cls = load_verifier_class(args.verifier, registry_data)
    verifier = verifier_cls()

    # 6) Read the poem
    with open(args.file, "r", encoding="utf-8") as f:
        poem_text = f.read()

    # 7) Build a dictionary of relevant args for the verifier
    #    We'll gather them from the JSON's argument definitions
    verifier_kwargs = {}
    for argdef in verifier_info.get("arguments", []):
        # e.g. "--tolerance"
        arg_name = argdef["name"].lstrip("-").replace("-", "_")  
        # If the name is "--tolerance", the attribute on 'args' is 'tolerance'
        verifier_kwargs[arg_name] = getattr(args, arg_name)

    # 8) Call verify or verify_with_feedback
    if args.feedback:
        result = verifier.verify_with_feedback(poem_text, **verifier_kwargs)
        score = result["score"]
        feedback_list = result["feedback"]
        print(f"Score: {score:.2f}")
        print("Feedback:")
        for msg in feedback_list:
            print(" -", msg)
    else:
        score = verifier.verify(poem_text, **verifier_kwargs)
        print(f"Score: {score:.2f}")

if __name__ == "__main__":
    main()

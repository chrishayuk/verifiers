import string

def is_n_words(answer, n=1, allow_punctuation=True):
    """
    Returns True if 'answer' contains exactly n words, optionally allowing punctuation.
    If allow_punctuation=False, words must be strictly alphanumeric.
    
    Parameters:
    -----------
    answer : str
        The string to be examined.
    n : int
        The exact number of words required.
    allow_punctuation : bool
        If True, punctuation is ignored in the sense that it counts as part 
        of a single word chunk. If False, punctuation is removed from the 
        answer before checking the word count, and each word must be alphanumeric.
    """
    # Trim leading/trailing whitespace
    trimmed = answer.strip()
    
    if not trimmed:
        return False  # empty or whitespace-only string can't have n words
    
    if allow_punctuation:
        # Split on whitespace and check the resulting number of chunks
        parts = trimmed.split()
        return len(parts) == n
    else:
        # Remove punctuation before splitting
        cleaned = "".join(ch for ch in trimmed if ch not in string.punctuation)
        parts = cleaned.strip().split()
        # Check that we have exactly n parts and that each part is alphanumeric
        return (len(parts) == n) and all(part.isalnum() for part in parts)


if __name__ == "__main__":
    # Some examples to test the function:
    examples = [
        ("Hello", 1),         # 1 word, no punctuation
        ("Hello!", 1),        # 1 word with punctuation
        ("Hello there", 2),   # exactly 2 words
        ("   Hello   ", 1),   # extra whitespace
        ("", 1),              # empty - should be False
        ("No,", 1),           # 1 word plus punctuation
        ("Spider-Man", 1),    # hyphenated - considered 1 word with punctuation
        ("Hello world!", 2),  # 2 words with punctuation
        ("One two three", 3), # 3 words
        ("A B C D", 4),       # 4 words
    ]
    
    for text, word_count in examples:
        result_allow = is_n_words(text, n=word_count, allow_punctuation=True)
        result_no_punc = is_n_words(text, n=word_count, allow_punctuation=False)
        print(f"Answer: '{text}' -> n={word_count}, allow_punctuation=True? {result_allow}; allow_punctuation=False? {result_no_punc}")

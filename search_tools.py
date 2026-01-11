from mock_db import MOCK_DB


def search(query: str, top_k: int = 7) -> list[dict]:
    """
    Search tool (stubbed).
    Returns a list of reference snippets.
    """
    import re

    # Stop words to ignore
    stop_words = {'and', 'or', 'if', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as',
                  'is', 'are', 'was', 'were'}

    query_lower = query.lower()
    query_terms = [term for term in query_lower.split() if term not in stop_words]

    results = []
    for r in MOCK_DB:
        # Search in both title and snippet
        text = f"{r['title']} {r['snippet']}".lower()
        text_words = re.findall(r'\b\w+\b', text)  # Extract whole words

        # Find which terms matched (whole word only)
        matched_terms = []
        for term in query_terms:
            # Use word boundary regex to match whole words only
            if re.search(r'\b' + re.escape(term) + r'\b', text):
                matched_terms.append(term)

        score = len(matched_terms)

        # Bonus points for phrase matching (2 words within 5 words)
        if len(query_terms) >= 2:
            for i in range(len(query_terms) - 1):
                word1 = query_terms[i]
                word2 = query_terms[i + 1]

                # Check if both words appear within 5 words of each other
                for j, text_word in enumerate(text_words):
                    if text_word == word1:
                        # Look in the next 5 words for word2
                        window = text_words[j:j + 6]
                        if word2 in window:
                            score += 2  # Bonus for phrase proximity
                            break

        if score > 0:
            results.append((score, matched_terms, r))

    # Sort by score (descending) and return top_k
    results.sort(reverse=True, key=lambda x: x[0])

    # Return results with their scores and matched terms
    return [
        {**r, "relevance_score": score, "matched_terms": matched_terms}
        for score, matched_terms, r in results[:top_k]
    ]
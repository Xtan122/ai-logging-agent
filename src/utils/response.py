def extract_response_text(response) -> str:
    """
    Extract plain text from various LLM response formats.

    Handles strings, lists of content blocks (dicts with 'text' key or bare
    strings), and any other object by falling back to str(). Always returns
    a stripped string so callers don't need to worry about leading/trailing
    whitespace.
    """
    text = ""
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and 'text' in block:
                    text_parts.append(block['text'])
                elif isinstance(block, str):
                    text_parts.append(block)
            text = '\n'.join(text_parts)
    else:
        text = str(response)
    return text.strip()
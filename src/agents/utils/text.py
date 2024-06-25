def get_content_between_a_b(start_tag, end_tag, text):
    """

    Args:
        start_tag (str): start_tag
        end_tag (str): end_tag
        text (str): complete sentence

    Returns:
        str: the content between start_tag and end_tag
    """
    extracted_text = ""
    start_index = text.find(start_tag)
    while start_index != -1:
        end_index = text.find(end_tag, start_index + len(start_tag))
        if end_index != -1:
            extracted_text += text[start_index + len(start_tag) : end_index] + " "
            start_index = text.find(start_tag, end_index + len(end_tag))
        else:
            break

    return extracted_text.strip()


def extract(text, type):
    """extract the content between <type></type>

    Args:
        text (str): complete sentence
        type (str): tag

    Returns:
        str: content between <type></type>
    """
    target_str = get_content_between_a_b(f"<{type}>", f"</{type}>", text)
    return target_str

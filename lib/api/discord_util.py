

def is_upscale(content: str):
    # string contains ' - Image #'
    return ' - Image #' in content


def is_variation(content: str):
    # string contains'Variation #'
    return 'Variation #' in content


def is_forward_action(content: str):
    return is_upscale(content) or is_variation(content)

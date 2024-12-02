def stringify_and_concatenate(data, threshold):
    """
    Stringifies a list and concatenates entries while keeping the total length below a given threshold.
    """
    result = []
    current_length = 0

    for item in data:
        item_str = str(item)
        if current_length + len(item_str) <= threshold:
            result.append(item_str)
            current_length += len(item_str)
        else:
            break

    return ''.join(result)
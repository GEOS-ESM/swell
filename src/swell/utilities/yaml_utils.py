
# --------------------------------------------------------------------------------------------------

def replace_key(obj, old_key, new_key):
    """
    Recursively replace dictionary keys in nested dictionaries/lists.
    """
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            new_k = new_key if k == old_key else k
            new_dict[new_k] = replace_key(v, old_key, new_key)
        return new_dict
    elif isinstance(obj, list):
        return [replace_key(item, old_key, new_key) for item in obj]
    else:
        return obj


def replace_string_value(data, sa, sb):
    """
    Recursively search through a dictionary or list and replaces specific
    sa by sb in the value content. sa/sb = string_a/b
    """
    if isinstance(data, dict):
        # If it's a dictionary, apply recursively to all values
        return {k: replace_string_value(v, sa, sb) for k, v in data.items()}

    elif isinstance(data, list):
        # If it's a list, apply recursively to all items
        return [replace_string_value(item, sa, sb) for item in data]

    elif isinstance(data, str):
        # If it's a string, check for our target keys and replace
        if sa in data:
            # Replaces sa with sb
            data = data.replace(sa, sb)
        return data
    else:
        # Return integers, booleans, etc., as-is
        return data


# --------------------------------------------------------------------------------------------------

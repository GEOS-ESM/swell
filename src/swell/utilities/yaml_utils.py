
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

# --------------------------------------------------------------------------------------------------

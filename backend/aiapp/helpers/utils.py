from collections.abc import Sequence

def estimate_tokens(estimation_obj):
  if isinstance(estimation_obj, str):
    return len(estimation_obj) // 4 + (1 if len(estimation_obj) % 4 != 0 else 0)
  if isinstance(estimation_obj, Sequence):
    total = 0
    for item in estimation_obj:
        # if it's a dict with a 'content' field, use that
        if isinstance(item, dict) and 'content' in item and isinstance(item['content'], str):
            total += estimate_tokens(item['content'])
        else:
            # otherwise recurse (handles nested lists, or strings directly)
            total += estimate_tokens(item)
    return total
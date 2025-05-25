

def estimate_tokens(line):
  return len(line) // 4 + (1 if len(line) % 4 != 0 else 0)
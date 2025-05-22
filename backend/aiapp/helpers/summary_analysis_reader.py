import json

def read_json_objects(file_path, separator="======"):
    """
    Generator that reads a file containing multiple JSON objects separated by a specific line.
    Yields one JSON object (as a dict) at a time.
    """
    with open(file_path, 'r') as f:
        buffer = []
        for line in f:
            if line.strip() == separator:
                if buffer:
                    raw_json = ''.join(buffer).strip()
                    try:
                        yield json.loads(raw_json)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON object: {e}")
                    buffer = []
            else:
                buffer.append(line)
        # Handle the last object if file doesn't end with separator
        if buffer:
            raw_json = ''.join(buffer).strip()
            try:
                yield json.loads(raw_json)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON object: {e}")

# Example usage
if __name__ == "__main__":
    file_path = "path/to/your/json_file.txt"
    for idx, obj in enumerate(read_json_objects(file_path), start=1):
        print(f"Object {idx}:")
        print(json.dumps(obj, indent=2))
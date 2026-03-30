import json
import os

DATA_DIR = "data"

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump([], f)
        return []
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []

def save_json(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def get_next_id(data):
    if not data:
        return 1
    return max(item.get('id', 0) for item in data) + 1

# --- Central Storage Functions ---

def add_record(filename, new_item):
    """Safely adds a new record to specified JSON file."""
    data = load_json(filename)
    new_item['id'] = get_next_id(data)
    data.append(new_item)
    save_json(filename, data)
    return new_item

def update_record(filename, item_id, updated_item):
    """Safely updates an existing record."""
    data = load_json(filename)
    for i, item in enumerate(data):
        if item.get('id') == item_id:
            updated_item['id'] = item_id
            data[i] = updated_item
            save_json(filename, data)
            return True
    return False

def delete_record(filename, item_id):
    """Safely deletes a record from the JSON store."""
    data = load_json(filename)
    original_len = len(data)
    data = [item for item in data if item.get('id') != item_id]
    if len(data) < original_len:
        save_json(filename, data)
        return True
    return False

def validate_data(item, required_fields):
    """Simple type validation and presence check."""
    for field, type_hint in required_fields.items():
        if field not in item:
            return False, f"Missing field: {field}"
        if not isinstance(item[field], type_hint):
            return False, f"Invalid type for {field}. Expected {type_hint.__name__}"
    return True, "Valid"

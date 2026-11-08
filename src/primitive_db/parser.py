
def parse_where(where_str):
    if not where_str:
        return None
    parts = where_str.split("=")
    if len(parts) != 2:
        raise ValueError("Неверный формат where")
    col = parts[0].strip()
    val = parts[1].strip().strip('"').strip("'")
    return {col: val}

def parse_set(set_str):
    parts = set_str.split("=")
    if len(parts) != 2:
        raise ValueError("Неверный формат set")
    col = parts[0].strip()
    val = parts[1].strip().strip('"').strip("'")
    return {col: val}

def parse_values(values_str):
    clean = values_str.strip("()")
    parts = [p.strip().strip('"').strip("'") for p in clean.split(",")]
    return parts
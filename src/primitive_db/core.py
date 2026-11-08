from .decorators import confirm_action, handle_db_errors


@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    
    full_columns = [{"name": "ID", "type": "int"}] + columns
    metadata[table_name] = {"columns": full_columns}
    print(f'Таблица "{table_name}" успешно создана со столбцами: ' + 
          ", ".join([f"{c['name']}:{c['type']}" for c in full_columns]))
    return metadata

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

@handle_db_errors
def insert(metadata, table_name, values):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    cols = metadata[table_name]["columns"]
    if len(values) != len(cols) - 1:
        print("Ошибка: Неверное количество значений.")
        return
    
    from .utils import load_table_data, save_table_data
    data = load_table_data(table_name)
    new_id = max([row["ID"] for row in data], default=0) + 1
    
    row = {"ID": new_id}
    for i, val in enumerate(values):
        row[cols[i+1]["name"]] = val
        
    data.append(row)
    save_table_data(table_name, data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

@handle_db_errors
def select(metadata, table_name, where_clause=None):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return []
    from .utils import load_table_data
    data = load_table_data(table_name)
    if where_clause:
        key = next(iter(where_clause.keys()))
        val = where_clause[key]
        data = [r for r in data if str(r.get(key)) == str(val)]
    return data

@handle_db_errors
def update(metadata, table_name, set_clause, where_clause):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    from .utils import load_table_data, save_table_data
    data = load_table_data(table_name)
    key_w = next(iter(where_clause.keys()))
    val_w = where_clause[key_w]
    key_s = next(iter(set_clause.keys()))
    val_s = set_clause[key_s]
    
    count = 0
    for row in data:
        if str(row.get(key_w)) == str(val_w):
            row[key_s] = val_s
            count += 1
    save_table_data(table_name, data)
    print(f"Обновлено записей: {count}")

@handle_db_errors
@confirm_action("удаление записи")
def delete(metadata, table_name, where_clause):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    from .utils import load_table_data, save_table_data
    data = load_table_data(table_name)
    key_w = next(iter(where_clause.keys()))
    val_w = where_clause[key_w]
    
    new_data = [r for r in data if str(r.get(key_w)) != str(val_w)]
    save_table_data(table_name, new_data)
    print(f'Запись с ID={where_clause.get("ID")} успешно удалена из таблицы "{table_name}".')
import shlex

from prettytable import PrettyTable

from .constants import META_FILE
from .core import create_table, delete, drop_table, insert, select, update
from .parser import parse_set, parse_values, parse_where
from .utils import load_metadata, save_metadata


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись")
    print("<command> select from <имя_таблицы> [where <столбец> = <значение>] - прочитать записи")
    print("<command> update <имя_таблицы> set <столбец> = <новое_значение> where <столбец> = <значение> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    print("\n***База данных***")
    print_help()
    
    metadata = load_metadata(META_FILE)
    
    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
            if not user_input:
                continue
                
            args = shlex.split(user_input)
            cmd = args[0].lower()
            
            if cmd == "exit":
                print("Выход из программы.")
                break
                
            elif cmd == "help":
                print_help()
                
            elif cmd == "list_tables":
                if not metadata:
                    print("Таблиц нет.")
                else:
                    for table in metadata:
                        print(f"- {table}")
                        
            elif cmd == "create_table":
                table_name = args[1]
                cols = []
                for col_str in args[2:]:
                    name, typ = col_str.split(":")
                    cols.append({"name": name, "type": typ})
                metadata = create_table(metadata, table_name, cols)
                save_metadata(META_FILE, metadata)
                
            elif cmd == "drop_table":
                table_name = args[1]
                new_meta = drop_table(metadata, table_name)
                if new_meta is not None:
                    metadata = new_meta
                    save_metadata(META_FILE, metadata)
                    
            elif cmd == "info":
                table_name = args[1]
                if table_name in metadata:
                    print(f"Таблица: {table_name}")
                    cols = ", ".join([f"{c['name']}:{c['type']}" for c in metadata[table_name]['columns']])
                    print(f"Столбцы: {cols}")
                    from .utils import load_table_data
                    print(f"Количество записей: {len(load_table_data(table_name))}")
                else:
                    print("Таблица не найдена.")
                    
            elif cmd == "insert" and args[1].lower() == "into":
                table_name = args[2]
                values_str = " ".join(args[4:])
                values = parse_values(values_str)
                insert(metadata, table_name, values)
                
            elif cmd == "select" and args[1].lower() == "from":
                table_name = args[2]
                where_clause = None
                if len(args) > 4 and args[3].lower() == "where":
                    where_clause = parse_where(" ".join(args[4:]))
                
                data = select(metadata, table_name, where_clause)
                if data:
                    table = PrettyTable()
                    table.field_names = [c["name"] for c in metadata[table_name]["columns"]]
                    for row in data:
                        table.add_row([row.get(c["name"], "") for c in metadata[table_name]["columns"]])
                    print(table)
                    
            elif cmd == "update":
                table_name = args[1]
                set_clause = parse_set(" ".join(args[3:args.index("where")]))
                where_clause = parse_where(" ".join(args[args.index("where")+1:]))
                update(metadata, table_name, set_clause, where_clause)
                
            elif cmd == "delete" and args[1].lower() == "from":
                table_name = args[2]
                where_clause = parse_where(" ".join(args[4:]))
                delete(metadata, table_name, where_clause)
                
            else:
                print(f"Функции <{cmd}> нет. Попробуйте снова.")
                
        except Exception as e: # noqa: BLE001
            print(f"Ошибка ввода: {e}")
import pandas as pd
import re
import gc
import duckdb

class DataManager:
    def __init__(self):
        self.all_files = {}  # { 'имя': dataframe }
        self.active_file_name = None

    def add_file(self, path):
        name = path.split('/')[-1]
        try:
            # engine='python' и sep=None заставляют Pandas автоматически определить ; или ,
            df = pd.read_csv(path, sep=None, engine='python', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(path, sep=None, engine='python', encoding='cp1251')
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return name, 0
        
        self.all_files[name] = df
        self.active_file_name = name
        return name, len(df)


    def get_active_df(self):
        return self.all_files.get(self.active_file_name)

    def rename_file(self, old_name, new_name):
        if old_name in self.all_files and new_name and old_name != new_name:
            self.all_files[new_name] = self.all_files.pop(old_name)
            if self.active_file_name == old_name:
                self.active_file_name = new_name
            return True
        return False

    def merge_selected(self, names):
        if not names: return None
        dfs = [self.all_files[n] for n in names if n in self.all_files]
        new_name = f"merged_{len(self.all_files)}.csv"
        self.all_files[new_name] = pd.concat(dfs, ignore_index=True, sort=False)
        self.active_file_name = new_name
        return new_name

    def clean_dropna(self):
        df = self.get_active_df()
        if df is not None:
            before = len(df)
            df.dropna(inplace=True)
            return before - len(df)
        return 0

    def extract_numbers(self, col_name):
        """Умное извлечение чисел (RegEx) из строки типа '33.5 кг' или '2,5'"""
        df = self.get_active_df()
        if df is not None and col_name in df.columns:
            pattern = r'(\d+[\.,]?\d*)'
            extracted = df[col_name].astype(str).str.extract(pattern)[0]
            df[col_name] = pd.to_numeric(extracted.str.replace(',', '.', regex=False), errors='coerce')
            return True
        return False
    
    def smart_merge(self, file_names, method='vertical', key_column=None):
        if not file_names or len(file_names) < 2:
            return "Нужно выбрать минимум 2 файла"
        selected_dfs = [self.all_files[name] for name in file_names if name in self.all_files]
        try:
            if method == 'vertical':
                result_df = pd.concat(selected_dfs, axis=0, ignore_index=True, sort=False)
            elif method == 'join':
                if not key_column: return "Укажите колонку-ключ для объединения"
                result_df = selected_dfs[0]
                for next_df in selected_dfs[1:]:
                    result_df = pd.merge(result_df, next_df, on=key_column, how='outer')
            
            master_name = f"Master_Result_{len(self.all_files)}.csv"
            self.all_files[master_name] = result_df
            self.active_file_name = master_name
            return f"Успешно! Создан файл: {master_name}"
        except Exception as e:
            return f"Ошибка объединения: {str(e)}"

    def delete_asset(self, file_name):
        """Удаление конкретного файла из памяти"""
        if file_name in self.all_files:
            del self.all_files[file_name]
            gc.collect()
            return True
        return False

    # --- НОВЫЕ МЕТОДЫ ДЛЯ ОПЕРАЦИЙ ---

    def delete_multiple_assets(self, file_names):
        """Массовое удаление отмеченных файлов"""
        for name in file_names:
            if name in self.all_files:
                del self.all_files[name]
        gc.collect()
        return True

    def apply_column_math(self, col1, col2, operation='*'):
        """Математика между столбцами активного файла"""
        df = self.get_active_df()
        if df is None: return False
        try:
            val1 = pd.to_numeric(df[col1], errors='coerce')
            val2 = pd.to_numeric(df[col2], errors='coerce')
            new_col = f"{col1}_{operation}_{col2}"
            if operation == '*':
                df[new_col] = val1 * val2
            elif operation == '-':
                df[new_col] = val1 - val2
            return True
        except Exception as e:
            print(f"Ошибка Math: {e}")
            return False
        
    def execute_sql(self, query):
        """
        Выполняет SQL запрос DuckDB над фреймворками в all_files.
        Важно: в SQL запросе имена таблиц должны быть в двойных кавычках: "file.csv"
        """
        try:
            # Создаем локальные переменные для DuckDB, чтобы он видел таблицы
            for name, df in self.all_files.items():
                locals()[name] = df
            
            # Выполняем запрос и конвертируем результат в Pandas DataFrame
            result_df = duckdb.query(query).to_df()
            
            # Регистрируем результат как новый актив
            new_name = f"SQL_Result_{len(self.all_files)}"
            self.all_files[new_name] = result_df
            self.active_file_name = new_name
            return new_name, None # Возвращаем имя и отсутствие ошибки
        except Exception as e:
            return None, str(e)

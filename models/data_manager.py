import pandas as pd
import re

class DataManager:
    def __init__(self):
        self.all_files = {}  # { 'имя': dataframe }
        self.active_file_name = None

    def add_file(self, path):
        name = path.split('/')[-1]
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding='cp1251', sep=None, engine='python')
        
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
            # Ищем число с точкой или запятой
            pattern = r'(\d+[\.,]?\d*)'
            extracted = df[col_name].astype(str).str.extract(pattern)[0]
            # Заменяем запятую на точку для Python и конвертируем в число
            df[col_name] = pd.to_numeric(extracted.str.replace(',', '.', regex=False), errors='coerce')
            return True
        return False
    

    def smart_merge(self, file_names, method='vertical', key_column=None):
        """
        file_names: список названий файлов из self.all_files
        method: 'vertical' (один под другой) или 'join' (по ключу)
        key_column: название колонки-ключа для 'join'
        """
        if not file_names or len(file_names) < 2:
            return "Нужно выбрать минимум 2 файла"

        selected_dfs = [self.all_files[name] for name in file_names]

        try:
            if method == 'vertical':
                # Просто ставим один под другой, сбрасываем индексы
                result_df = pd.concat(selected_dfs, axis=0, ignore_index=True)
                
            elif method == 'join':
                if not key_column:
                    return "Укажите колонку-ключ для объединения"
                
                # Начинаем с первого файла и по цепочке приклеиваем остальные
                result_df = selected_dfs[0]
                for next_df in selected_dfs[1:]:
                    # how='outer' сохранит все данные из обоих файлов
                    result_df = pd.merge(result_df, next_df, on=key_column, how='outer')

            # Сохраняем результат как новый "виртуальный" файл
            master_name = f"Master_Result_{len(self.all_files)}"
            self.all_files[master_name] = result_df
            return f"Успешно! Создан файл: {master_name}"

        except Exception as e:
            return f"Ошибка объединения: {str(e)}"

    def delete_asset(self, file_name):
        """Удаление конкретного файла из памяти"""
        if file_name in self.all_files:
            del self.all_files[file_name]
            return True
        return False


import os

from data_importer import DataImporter
from screen_handler import State


class ImportScreen(State):

    def __init__(self):
        super()
        self.data_importer = DataImporter()
        print('[!] Choose a database to import (write down):')
        self.print_databases()
        self.current_stage = 'select_db'

        self.stages = {
            'select_db': self.handle_select_db,
            'import_tables': self.handle_import_tables
        }

    def print_databases(self):
        databases = self.data_importer.get_databases()

        for db in databases:
            print(f'\t[*] {db}')

    def handle_select_db(self, database: str):
        self.data_importer.set_database(database)
        tables = self.data_importer.get_tables()

        print(f'[!] Select tables to import (separated by commas):')

        for table in tables:
            print(f'\t[*] {table}')

        self.current_stage = 'import_tables'

    def handle_import_tables(self, tables_str: str):
        tables = list(map(lambda x: x.strip(), tables_str.split(',')))
        project_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'imported')
        project_path = os.path.abspath(project_path)

        print('[!] Set a path to save the imported data.')
        path = str(input(f'(default={project_path}): ')).strip()

        if path == '':
            path = project_path

        print(f'[!] importing tables {str(tables)}')
        self.data_importer.import_tables(tables, path)

    def handle_option(self, option) -> None:
        stage_function = self.stages[self.current_stage]
        stage_function(option)


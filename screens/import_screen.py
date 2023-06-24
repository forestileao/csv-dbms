import os

from data_importer import DataImporter
from screen_handler import State


class ImportScreen(State):

    def __init__(self):
        super()
        self.data_importer = DataImporter()
        self.current_stage = 'select_db_type'

        self.stages = {
            'select_db_type': self.handle_select_db_type,
            'select_db': self.handle_select_db,
            'import_tables': self.handle_import_tables
        }

    def handle_select_db_type(self, database_type: str):
        if database_type not in ["postgres", "mysql", "csv"]:
            raise ("Invalid option setting database_type")
            self.context.return_last_state()

        self.data_importer.set_database_type(database_type)
        self.current_stage = 'select_db'

    def handle_select_db(self, database: str):
        if database not in self.data_importer.get_databases():
            print("Database does not exist. Aborting.")
            return

        self.data_importer.set_database(database)
        self.tables = self.data_importer.get_tables()

        self.current_stage = 'import_tables'

    def handle_import_tables(self, tables_str: str):

        tables = list(map(lambda x: x.strip(), tables_str.split(','))) if tables_str != "" else self.data_importer.get_tables()

        print(list(set(tables) & set(self.data_importer.get_tables())))

        # Check if there is a intersection between tables inserted and the ones on database
        if tables_str != "*" and len(list(set(tables) & set(self.data_importer.get_tables()))) <= 0:
            print("Table does not exist. Aborting.")
            return

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

        print(f'Imported Successfully.')
        self.context.return_last_state()

    def handle_option(self, option) -> None:
        stage_function = self.stages[self.current_stage]
        stage_function(option)

    def print_options(self):
        if self.current_stage == "select_db_type":
            print('[!] Choose the type of import (write down):')
            print(f'\t[*] postgres')
            print(f'\t[*] mysql')
            print(f'\t[*] csv')

        elif self.current_stage == "select_db":
            print('[!] Choose a database to import from (write down):')
            databases = self.data_importer.get_databases()

            for db in databases:
                print(f'\t[*] {db}')

        elif self.current_stage == "import_tables":
            print(f'[!] Select tables to import (separated by commas) or "*" to import all):')

            if len(self.tables) == 0:
                print("\t0 Tables found...")
                self.context.return_last_state()

            for table in self.tables:
                print(f'\t[*] {table}')

        else:
            raise ("Internal error: Import menu stage missing.")



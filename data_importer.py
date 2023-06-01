import psycopg2
import os
import csv


class DataImporter:

    def __init__(self):
        self.db_client = psycopg2.connect(
            user=os.getenv('POSTGRESQL_USER'),
            password=os.getenv('POSTGRESQL_PASSWORD'),
            host=os.getenv('POSTGRESQL_HOST'),
            port=os.getenv('POSTGRESQL_PORT')
        )

    def get_databases(self) -> list:
        cursor = self.db_client.cursor()
        cursor.execute('SELECT datname FROM pg_database WHERE datistemplate = false;')

        databases = [row[0] for row in cursor.fetchall()]
        cursor.close()

        return databases

    def set_database(self, database: str) -> None:
        self.db_client.close()
        self.db_client = psycopg2.connect(
            user=os.getenv('POSTGRESQL_USER'),
            password=os.getenv('POSTGRESQL_PASSWORD'),
            host=os.getenv('POSTGRESQL_HOST'),
            port=os.getenv('POSTGRESQL_PORT'),
            dbname=database
        )

    def get_tables(self) -> list:
        cursor = self.db_client.cursor()

        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        table_list = [row[0] for row in cursor.fetchall()]
        cursor.close()

        return table_list

    def import_table(self, table: str, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)

        cursor = self.db_client.cursor()
        cursor.execute(f'select * from {table};')
        columns = tuple([desc[0] for desc in cursor.description])
        data = cursor.fetchall()

        cursor.close()

        data.insert(0, columns)

        output_path = os.path.join(output_dir, table + '.csv')
        self.save_tuples_to_csv(output_path, data)
        
    def import_tables(self, tables: list, output_dir: str) -> None:
        for table in tables:
            self.import_table(table, output_dir)

    @staticmethod
    def save_tuples_to_csv(output_path, tuples_list):
        with open(output_path, 'w') as f:
            write = csv.writer(f)
            write.writerows(tuples_list)

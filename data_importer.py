import psycopg2
import mysql.connector
import os
import csv


class DataImporter:

    def __init__(self):
        self.db_client = None
        self.database_type = ''
        self.database = ''

    def get_databases(self) -> list:
        cursor = self.db_client.cursor()
        if self.database_type == "postgres":
            cursor.execute('SELECT datname FROM pg_database WHERE datistemplate = false;')
        elif self.database_type == "mysql":
            cursor.execute('SHOW DATABASES;')
        else:
            raise ("Error connecting to database: NO DATABASE TYPE SET")

        databases = [row[0] for row in cursor.fetchall()]
        cursor.close()

        return databases

    def set_database_type(self, database_type: str):
        self.database_type = database_type

        if self.database_type == "postgres":
            self.db_client = psycopg2.connect(
                host=os.getenv('POSTGRESQL_HOST'),
                port=os.getenv('POSTGRESQL_PORT'),
                user=os.getenv('POSTGRESQL_USER'),
                password=os.getenv('POSTGRESQL_PASSWORD')
            )
        elif self.database_type == "mysql":
            self.db_client = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST'),
                port=os.getenv('MYSQL_PORT'),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD')
            )
        elif self.database_type == "csv":
            print("TODO: CSV selected")
        else:
            raise ("Error connecting to database: NO DATABASE TYPE SET")

    def set_database(self, database: str) -> None:
        self.db_client.close()
        self.database = database
        if self.database_type == "postgres":
            self.db_client = psycopg2.connect(
                host=os.getenv('POSTGRESQL_HOST'),
                port=os.getenv('POSTGRESQL_PORT'),
                user=os.getenv('POSTGRESQL_USER'),
                password=os.getenv('POSTGRESQL_PASSWORD'),
                dbname=database
            )
        elif self.database_type == "mysql":
            self.db_client = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST'),
                port=os.getenv('MYSQL_PORT'),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=database
            )
        else:
            raise("Error connecting to database: NO DATABASE TYPE SET")

    def get_tables(self) -> list:
        cursor = self.db_client.cursor()

        if self.database_type == "postgres":
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")

        elif self.database_type == "mysql":
            cursor.execute("SHOW TABLES;")

        else:
            raise ("Error connecting to database: NO DATABASE TYPE SET")

        table_list = [row[0] for row in cursor.fetchall()]
        cursor.close()

        return table_list

    def import_table(self, table: str, output_dir: str, database: str) -> None:
        output_dir = os.path.join(output_dir, database)
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
            self.import_table(table, output_dir, self.database)

    @staticmethod
    def save_tuples_to_csv(output_path, tuples_list):
        with open(output_path, 'w') as f:
            write = csv.writer(f)
            write.writerows(tuples_list)

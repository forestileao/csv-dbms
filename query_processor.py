import os
import csv
import sys


class QueryProcessor:
    reserved_keywords = ["select", "from", "join", "where", "order", "by", "on", "using", "create", "insert"]
    comparison_operands = ["=", "<", ">", "<=", ">=", "<>"]

    def __init__(self):
        self.database = ''

        project_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'imported')
        self.project_path = os.path.abspath(project_path)

        print('[!] Set a path to load the imported data.')
        self.project_path = str(input(f'(default={project_path}): ')).strip()

        if self.project_path == '':
            self.project_path = project_path
        self.path = ''

    def process(self, query):

        queries = query.split(';')

        for query in queries:

            query = query.strip()

            if len(query) != 0:

                if query.startswith('use'):
                    _, database = query.split(' ')
                    self.database = database
                    self.path = os.path.join(self.project_path, self.database)
                elif self.database != '':
                    self.parse_query(query)
                else:
                    print('[!] First, select a database! (use DATABASE_NAME)')

    def parse_query(self, query):
        original_query = query
        query_params = []
        param_start = query.find("'")
        while (param_start != -1):
            param_end = param_start + query[param_start + 1:].find("'") + 1
            parameter = query[param_start + 1:param_end]
            query_params.append(parameter)
            query = query.replace(f"'{parameter}'", '?')
            param_start = query.find("'")

        tokens = query.lower().split(' ')
        tokens = list(filter(lambda item: item != '', tokens))

        for i in range(len(tokens)):
            if '?' in tokens[i]:
                tokens[i] = "\'" + query_params[0] + "\'"
                query_params.pop(0)

        try:
            tables = self.get_tables(tokens)
            ordination = self.ordination(tokens)
            filters = self.get_filters(tokens)
            columns = self.select_columns(tokens)

            loaded_dada = self.load_tables(tables)

            if filters is not None:
                loaded_dada = self.apply_filters(loaded_dada, filters)

            if columns is not None:
                loaded_dada = self.select(loaded_dada, columns)

            if ordination is not None:
                loaded_dada = self.order_by(loaded_dada, ordination)

            if len(loaded_dada) != 0:
                self.print_csv_from_dict_list(loaded_dada)
            else:
                print('No data!')

        except Exception as e:
            print(f"Exception while processing query:\n{original_query}\n{e}")

    def get_tables(self, tokens):
        tables = []

        for i in range(len(tokens)):
            if tokens[i] in ["from", "join"]:

                # Checks if the name of the table exists, and it's not a reserved keyword
                if i + 1 >= len(tokens) or tokens[i + 1] in self.reserved_keywords:
                    raise Exception("Error on SQL syntax")

                if tokens[i] == 'join':
                    joining_table = tokens[i + 1]
                    using_param = tokens[i + 2].replace('using(', '').replace(')', '')
                    tables.append((joining_table, using_param))
                else:
                    tables.append(tokens[i + 1])

        return tables

    def get_filters(self, tokens):

        variables = []
        filters = []

        if "where" in tokens:
            index = tokens.index("where")

            for i in range(index + 1, len(tokens)):
                if tokens[i] in self.reserved_keywords:
                    break

                if tokens[i] in self.comparison_operands:  # Evaluating the variable
                    variables.append(tokens[i - 1])

                filters.append(tokens[i])

        if len(filters) == 0:
            return None

        return filters

    def ordination(self, tokens):
        if "order" in tokens:
            order_pos = tokens.index("order")
            if tokens[order_pos + 1] != "by" or tokens[order_pos + 2] in self.reserved_keywords:
                raise Exception("Error on SQL syntax")

            return tokens[order_pos + 2]
        else:
            return None

    def select_columns(self, tokens):
        columns = []

        if "select" in tokens:
            index = tokens.index("select") + 1

            if tokens[index] == '*':
                return None

            while tokens[index] != "from":
                field = tokens[index].replace(',', '')
                columns.append(field)
                index += 1

        return columns

    def load_tables(self, tables):
        result = []
        for table in tables:
            if isinstance(table, str):
                table_path = os.path.join(self.path, table + '.csv')
                table_data = self.load_csv_as_dict(table_path)

                if len(result) == 0:
                    result = table_data
                elif len(table_data) != 0:
                    result = [{**d1, **d2} for d1 in result for d2 in table_data]
            elif isinstance(table, tuple) and len(table) == 2:
                table_name, join_column = table
                table_path = os.path.join(self.path, table_name + '.csv')
                table_data = self.load_csv_as_dict(table_path)

                result = [{**d1, **d2} for d1 in result for d2 in table_data if d1.get(join_column) == d2.get(join_column)]

        return result

    def load_csv_as_dict(self, path):
        result = []

        with open(path, 'r', newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                result.append(dict(row))

        return result

    def print_csv_from_dict_list(self, dict_list):
        keys = dict_list[0].keys()

        csv_writer = csv.DictWriter(sys.stdout, fieldnames=keys)
        csv_writer.writeheader()

        for dictionary in dict_list:
            csv_writer.writerow(dictionary)

    @staticmethod
    def select(data: list[dict], fields: list):
        if fields is None:
            return data

        result = []

        for row in data:
            selected_row = {}

            for field in fields:
                if field in row:
                    selected_row[field] = row[field]

            result.append(selected_row)

        return result

    @staticmethod
    def order_by(data: list, field: str):
        reverse = False
        if field.startswith('-'):
            field = field[1:]
            reverse = True

        return sorted(data, key=lambda x: x[field], reverse=reverse)

    def apply_filters(self, data: list, filters: list):

        unique_filter = len(filters) == 3
        contains_and = 'and' in filters
        and_predicates = self.split_list(filters, 'and') if contains_and or unique_filter else []
        def is_and_valid(row):
            and_valid = True
            for field, operator, value in and_predicates:
                value = int(value) if value.isnumeric() else value.replace("'", "")
                row[field] = int(row[field]) if row[field].isnumeric() else row[field]
                if operator == '=':
                    if row[field] != value:
                        and_valid = False
                        break
                elif operator == '!=':
                    if row[field] == value:
                        and_valid = False
                        break
                elif operator == '>=':
                    if row[field] < value:
                        and_valid = False
                        break
                elif operator == '<=':
                    if row[field] > value:
                        and_valid = False
                        break
                elif operator == '>':
                    if row[field] <= value:
                        and_valid = False
                        break
                elif operator == '<':
                    if row[field] >= value:
                        and_valid = False
                        break
            if and_valid:
                return True
            return False

        contains_or = 'or' in filters
        or_predicates = self.split_list(filters, 'or') if contains_or else []

        def is_or_valid(row):
            or_valid = False
            for field, operator, value in or_predicates:
                value = int(value) if value.isnumeric() else value.replace("'", "")
                row[field] = int(row[field]) if row[field].isnumeric() else row[field]
                if operator == '=':
                    if row[field] == value:
                        or_valid = True
                        break
                elif operator == '!=':
                    if row[field] != value:
                        or_valid = True
                        break
                elif operator == '>=':
                    if row[field] >= value:
                        or_valid = True
                        break
                elif operator == '<=':
                    if row[field] <= value:
                        or_valid = True
                        break
                elif operator == '>':
                    if row[field] > value:
                        or_valid = True
                        break
                elif operator == '<':
                    if row[field] < value:
                        or_valid = True
                        break
            if or_valid:
                return True
            return False

        filtered = []
        for row in data:
            if (contains_and or unique_filter) and is_and_valid(row):
                filtered.append(row)
            elif contains_or and is_or_valid(row):
                filtered.append(row)

        return filtered

    def split_list(self, lst, value):
        result = []
        sublist = []

        for item in lst:
            if item == value:
                if sublist:
                    result.append(sublist)
                    sublist = []
            else:
                sublist.append(item)

        if sublist:
            result.append(sublist)

        return result


if __name__ == "__main__":
    query = "select course_id, title, dept_name from course join section using(course_id) where course_id = 'BIO-101' and credits >= 4"
    print(query)

    aa = QueryProcessor()
    aa.process('use dbbook')
    aa.process(query=query)

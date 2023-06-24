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
                    return

    def parse_query(self, query):
        original_query = query

        if 'insert into' in query:
            tokens = self.get_insert_tokens(query)
            operation_type = 'insert'
        else :
            tokens = self.get_query_tokens(query)
            operation_type = 'query'

        try:
            if operation_type == 'insert':
                self.handle_insert(tokens)
            elif operation_type == 'query':
                self.handle_query(tokens)

        except Exception as e:
            print(f"Exception while processing query:\n{original_query}\n{e}")


    def handle_query(self, query_tokens):
        tables = self.get_tables(query_tokens)
        ordination = self.ordination(query_tokens)
        filters = self.get_filters(query_tokens)
        columns = self.select_columns(query_tokens)

        loaded_dada = self.load_tables(tables)

        if filters is not None:
            loaded_dada = self.apply_filters(loaded_dada, filters)

        if ordination is not None:
            loaded_dada = self.order_by(loaded_dada, ordination)

        if columns is not None:
            loaded_dada = self.select(loaded_dada, columns)

        if len(loaded_dada) != 0:
            self.print_csv_from_dict_list(loaded_dada)
        else:
            print('No data!')

    def get_insert_tokens(self, query: str):
        query = query.replace('insert into ', '')
        table_data, values = query.split('values')
        table = table_data.strip()
        values_array = values.strip().split('),')

        new_rows = []
        for row in values_array:
            row_values = row.replace("'", "").replace('(', '').replace(')', '').split(',')

            adding_row = []
            for row_value in row_values:
                adding_row.append(row_value.strip())

            new_rows.append(','.join(adding_row))

        rows_string = '\n'.join(new_rows) + '\n'
        return table, rows_string

    def get_query_tokens(self, query):
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

        return tokens

    def get_tables(self, tokens):
        tables = []

        for i in range(len(tokens)):
            if tokens[i] in ["from", "join"]:

                # Checks if the name of the table exists, and it's not a reserved keyword
                if i + 1 >= len(tokens) or tokens[i + 1] in self.reserved_keywords:
                    raise Exception("Error on SQL syntax")

                if tokens[i] == 'join':
                    joining_table = tokens[i + 1]

                    if "using" in tokens[i+2]:
                        using_param = tokens[i + 2].replace('using(', '').replace(')', '')
                        tables.append((joining_table, using_param))

                    elif "on" in tokens[i + 2]:
                        curr_index = i+2
                        complete_expression = ""

                        while "=" not in tokens[curr_index]:
                            complete_expression += tokens[curr_index]
                            curr_index += 1

                        complete_expression += tokens[curr_index]

                        if complete_expression[-1] == "=":
                            curr_index += 1
                            complete_expression += tokens[curr_index]

                        if complete_expression[0:2] == "on":
                            complete_expression = complete_expression[2:]

                        args1, args2 = complete_expression.replace(')', '').replace('(',  '').split('=')

                        table1, column1 = args1.split('.')
                        table2, column2 = args2.split('.')
                        tables.append((table1, column1, table2, column2))

                    else:
                        raise Exception("Error on SQL syntax")

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

            elif isinstance(table, tuple) and len(table) == 4:
                table1, column1, table2, column2 = table
                table_path = os.path.join(self.path, table2 + '.csv')
                table_data = self.load_csv_as_dict(table_path)

                result = [{**d1, **d2} for d1 in result for d2 in table_data if d1.get(column1) == d2.get(column2)]

        return result

    def handle_insert(self, tokens):
        table, values_str = tokens

        inserting_path = os.path.join(self.path, table + '.csv')
        with open(inserting_path, "a") as f:
            f.write(values_str)

            print('Insert finished with success!')

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

        return sorted(data, key=lambda x: float(x[field]) if x[field].isnumeric() else x[field], reverse=reverse)

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
    # query = "select course_id, title, dept_name from course join section using(course_id) where course_id = 'BIO-101' and credits >= 4"
    query = "select course_id, title, dept_name from course join section on(course.course_id=section.course_id) where course_id = 'BIO-101' and credits >= 4"
    print(query)

    aa = QueryProcessor()
    aa.process('use postgres')
    aa.process(query=query)

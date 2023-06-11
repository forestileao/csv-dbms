class QueryProcessor:

    reserved_keywords = ["select", "from", "join", "where", "order", "by", "on", "using", "create", "insert"]
    comparison_operands = ["=", "<", ">", "<=", ">=", "<>"]
    def __init__(self):
        pass

    def process(self, query):

        original_query = query
        query_params = []

        query = query.lower()

        param_start = query.find("'")
        while (param_start != -1):
            param_end = param_start + query[param_start + 1:].find("'") + 1
            parameter = query[param_start + 1:param_end]
            query_params.append(parameter)
            query = query.replace(f"'{parameter}'", '?')
            param_start = query.find("'")

        tokens = query.split(' ')
        tokens = list(filter(lambda item: item != '', tokens))

        for i in range(len(tokens)):
            if '?' in tokens[i]:
                tokens[i] = "\'" + query_params[0] + "\'"
                query_params.pop(0)

        try:
            tables = self.get_tables(tokens)
            print(f"Joining tables {tables}")

            ordination = self.ordination(tokens)
            print(f"Order by {ordination}")

            filters = self.get_filters(tokens)
            print(f"Filtering by {filters}")

            columns = self.select_columns(tokens)
            print(f"select {columns}")

        except Exception as e:
            print(f"Exception while processing query:\n{original_query}\n{e}")


    def get_tables(self, tokens):
        tables = []

        for i in range(len(tokens)):
            if tokens[i] in ["from", "join"]:

                # Checks if the name of the table exists, and it's not a reserved keyword
                if i + 1 >= len(tokens) or tokens[i + 1] in self.reserved_keywords:
                    raise Exception("Error on SQL syntax")
                    return []

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
                    variables.append(tokens[i-1])

                filters.append(tokens[i])

        variables = ['x.' + x for x in variables]

        filter_str = ' '.join(filters)

        print(filter_str)

        lamb_func = lambda x: eval(filter_str)

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

            while tokens[index] != "from":
                field = tokens[index].replace(',', '')
                columns.append(field)
                index += 1

        return columns


if __name__ == "__main__":
    query = "select a, b, c from pedro p join teste t using id join pinhao using id where name = 'matheus burda' and id >= 8 order by '-id'"

    print(query)

    aa = QueryProcessor()
    aa.process(query=query)
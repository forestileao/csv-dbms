class QueryProcessor:
    def __init__(self):
        pass

    def process(self, query):
        # antes do loop
        query_params = []
        query = "select * from pastel where id = 'caraio burracha mano' and x = '76'"

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
                tokens[i] = query_params[0]
                query_params.pop(0)


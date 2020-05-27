import json


class Function:
    def __init__(self, alias, method):
        self.alias = alias
        self.method = method

    def __call__(self, *args, **kwargs):
        return self.method(*args)


class Functions:
    """
    Function manager exposed as a dictionary to keep track of all registered functions and create a
    combined schema.
    """

    def __init__(self, *args):
        self.functions = {}

    def __setitem__(self, key, value):
        assert isinstance(value, Function)
        self.functions[key.lower()] = value

    def __getitem__(self, key):
        return self.functions[key.lower()]

    def render_evaluate(self, request, do_print=True):
        """
        # POST /evaluate
        tables.render_evaluate()
        """
        jreq = json.loads(request)

        if 'function' not in jreq['body']:
            raise ValueError(f"<function> field is expected to evaluate method -> {jreq['body']}")

        function_name = jreq['body']['function']

        if 'data' not in jreq['body']:
            raise ValueError(f"<data> field is expected to evaluate method -> {jreq['body']}")

        arg_dict = jreq['body']['data']

        function = self[function_name.lower()]
        ret_value = list()

        arg_dict_values = [value for key, value in sorted(arg_dict.items())]

        for arg_values in zip(*arg_dict_values):
            try:
                invoke_result = function(*arg_values)
                ret_value.append(invoke_result)
            except Exception as e:
                ret_value.append(str(e))

        json_return = json.dumps(ret_value)

        if do_print:
            print(json_return)
        else:
            return json_return

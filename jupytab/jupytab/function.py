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

        if not 'data' in jreq['body']:
            raise ValueError('Data field is expected to evaluate method')

        arg_dict = jreq['body']['data']

        if not 'script' in jreq['body']:
            raise ValueError('Script field is expected to evaluate method')

        function_name = jreq['body']['script']

        function = self[function_name]

        ret_value = function(arg_dict.values())

        if do_print:
            print(ret_value)
        else:
            return ret_value
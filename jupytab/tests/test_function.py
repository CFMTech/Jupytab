import json

from jupytab.function import Functions, Function


def test_function():
    def no_arg_function():
        return True

    def check_eq_10(arg_1):
        return arg_1 == 10

    def product(arg_1, arg_2):
        return arg_1 * arg_2

    def multi_add(*args):
        return sum(*args)

    f_no_arg = Function("No arguments", no_arg_function)
    f_check_eq_10 = Function("Check value equals 10", check_eq_10)
    f_product = Function("Product of two arguments", product)
    f_multi_add = Function("Sum of all arguments", multi_add)

    assert f_no_arg()
    assert not f_check_eq_10(5)
    assert f_check_eq_10(10)
    assert f_product(3, 5) == 15
    assert f_multi_add(range(1, 10)) == 45


def test_multi_add():
    def multi_add(*args):
        return sum(args)

    funcs = Functions()
    funcs['MultiAdd'] = Function("Sum of all arguments", multi_add)

    request = json.dumps({
        "body": {
            "function": "MultiAdd",
            "data": {
                "_arg1": list(range(1, 10)),
                "_arg2": list(range(1, 10))
            }
        }
    })

    x = funcs.render_evaluate(request, do_print=False)
    assert x == "[2, 4, 6, 8, 10, 12, 14, 16, 18]"


def test_typed_method():
    def typed_method(a_int, a_float, a_string, a_bool):
        check_type = \
            isinstance(a_int, int) and \
            isinstance(a_float, float) and \
            isinstance(a_string, str) and \
            isinstance(a_bool, bool)

        return check_type

    funcs = Functions()
    funcs['TypedMethod'] = Function("Typed method", typed_method)

    request = json.dumps({
        "body": {
            "function": "TypedMethod",
            "data": {
                "_arg4": [True],
                "_arg2": [2.5],
                "_arg3": ["Test"],
                "_arg1": [10]
            }
        }
    })

    x = funcs.render_evaluate(request, do_print=False)
    assert x == "[true]"

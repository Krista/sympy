from __future__ import print_function, division
from sympy.core import Mul, Pow, S, Rational
from sympy.core.compatibility import string_types, range
from sympy.core.mul import _keep_coeff
from sympy.codegen.ast import Assignment
from sympy.printing.codeprinter import CodePrinter
from sympy.printing.precedence import precedence, PRECEDENCE
from re import search

known_fcns_src1 = ["sin", "cos", "tan", "cot", "sec", "csc",
                   "asin", "acos", "acot", "atan", "atan2", "asec", "acsc",
                   "sinh", "cosh", "tanh", "coth", "csch", "sech",
                   "asinh", "acosh", "atanh", "acoth", "asech", "acsch",
                   "erfc", "erfi", "erf", "erfinv", "erfcinv",
                   "besseli", "besselj", "besselk", "bessely",
                   "exp", "factorial", "floor", "fresnelc", "fresnels",
                   "gamma", "log", "polylog", "sign", "zeta"]

operation_dict = {
    'Add': '+',
    'Mul': '*',
    'Rational': '/',
    'Pow': 'expt',
    'Abs': 'abs',
    'Eq': 'eql',
    'Div': 'rem',
    # 'Mod': 'mod',

}

class LispCodePrinter(CodePrinter):
    """
    A printer to convert arithmetic expressions to strings of Lisp code
    in full bracket style in prefix format
    """
    printmethod = "_lisp"
    language = "Lisp"

    _operators = {
        'and': '&',
        'or': '|',
        'not': '~',
    }

    _default_settings = {
        'order': None,
        'full_prec': 'auto',
        'precision': 16,
        'user_functions': {},
        'human': True,
        'contract': True,
        'inline': True,
    }

    def __init__(self, settings={}):
        super(LispCodePrinter, self).__init__(settings)
        self.known_functions = dict(zip(known_fcns_src1, known_fcns_src1))
        self.known_functions.update(dict(operation_dict))
        userfuncs = settings.get('user_functions', {})
        self.known_functions.update(userfuncs)

    output = ""
    def lisp(self, expr):
        if not isinstance(expr, Basic):
            print(expr)
        global output
        output = ""
        self._toPrefix(expr)
        print(output)

    def _toPrefix(self, expr):
        global output
        if expr.is_Atom:
            if expr.is_rational:
                output += self.print_rational(expr, "Rational")
            else:
                output += str(expr) + " "
        else:
            name = expr.__class__.__name__
            for i in expr.args[:-1]:
                output += "("
                lisp_name = operation_dict.get(name)
                if lisp_name is not None:
                    output += lisp_name + " "
                else:
                    output += name.lower() + " "
                self._toPrefix(i)
            self._toPrefix(expr.args[-1])
            output += ") " * (len(expr.args)-1)


    def print_rational(self, expr, op):
        _string = "( " + operation_dict.get(op) + " " + str(expr.p) + " " + str(expr.q) + ") "
        return _string



def lisp_code(expr, assign_to=None, **settings):
    r"""Converts `expr` to a string of Lisp code.

    Parameters
    ==========

    expr : Expr
        A sympy expression to be converted.
    assign_to : optional
        When given, the argument is used as the name of the variable to which
        the expression is assigned.  Can be a string, ``Symbol``,
        ``MatrixSymbol``, or ``Indexed`` type.  This can be helpful for
        expressions that generate multi-line statements.
    precision : integer, optional
        The precision for numbers such as pi  [default=16].
    user_functions : dict, optional
        A dictionary where keys are ``FunctionClass`` instances and values are
        their string representations.  Alternatively, the dictionary value can
        be a list of tuples i.e. [(argument_test, cfunction_string)].  See
        below for examples.
    human : bool, optional
        If True, the result is a single string that may contain some constant
        declarations for the number symbols.  If False, the same information is
        returned in a tuple of (symbols_to_declare, not_supported_functions,
        code_text).  [default=True].
    contract: bool, optional
        If True, ``Indexed`` instances are assumed to obey tensor contraction
        rules and the corresponding nested loops over indices are generated.
        Setting contract=False will not generate loops, instead the user is
        responsible to provide values for the indices in the code.
        [default=True].
    inline: bool, optional
        If True, we try to create single-statement code instead of multiple
        statements.  [default=True].

    Examples:

    from sympy import lisp_code, symbols, sin, pi
    from sympy.abc import x,y,z,A,B,C,D,E
    example = lisp_code((x - 2*x**2 +1) % 4)
    print("\n")
    example2 = lisp_code((A+B**C)*D+E**5)
    """

    return LispCodePrinter(settings).doprint(expr, assign_to)


def print_lisp_code(expr, **settings):
    """Prints the Lisp representation of the given expression.

    See `lisp_code` for the meaning of the optional arguments.
    """
    print(lisp_code(expr, **settings))
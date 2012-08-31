"""
Decorators for validating function/members argument and return types.

Example:
    @accepts(int, int, int)
    @returns(float)
    def average(x, y, z):
        return (x + y + z) / 2
        average(5.5, 10, 15.0)

    class Test(object):
        @accepts(IGNORE, int)
        @returns(int)
        def return_arg(self, int_var):
            return int_var

Read more:
    http://wiki.python.org/moin/PythonDecoratorLibrary#Type_Enforcement_.28accepts.2BAC8-returns.29

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

class IGNORE():
    """Used to ignore an accept parameter, for example self."""

def decorator_type(arg):
    if hasattr(arg, "__class__"):
        return arg.__class__
    else:
        return type(arg)

def accepts(*types, **kw):
    """
    Function decorator. Checks that inputs given to decorated function
    are of the expected type.

    Parameters:
    types -- The expected types of the inputs to the decorated function.
             Must specify type for each parameter. Use type "object"
             for self on class members.

    """
    def decorator(f):
        def newf(*args, **kw):
            assert len(kw) == 0 # we dont support accept keyargument
            arglist = list(map(decorator_type, args))

            # If decorated function is a member of a class ignore
            for i in xrange(len(types)):
                if types[i] == IGNORE:
                    if i <= len(arglist)-1:
                        arglist[i] = IGNORE
                    else:
                        arglist.append(IGNORE)

            argtypes = tuple(arglist)
            if argtypes != types:
                msg = _info(f.__name__, types, argtypes, 0)
                raise TypeError, msg

            return f(*args, **kw)

        newf.__name__ = f.__name__
        return newf

    return decorator


def returns(ret_type, **kw):
    """
    Function decorator. Checks that return value of decorated function
    is of the expected type.

    Parameters:
    ret_type -- The expected type of the decorated function's return value.
                Must specify type for each parameter.

    """
    def decorator(f):
        def newf(*args):
            result = f(*args)
            res_type = decorator_type(result)
            if res_type != ret_type:
                msg = _info(f.__name__, (ret_type,), (res_type,), 1)
                raise TypeError, msg
            return result
        newf.__name__ = f.__name__
        return newf
    return decorator


def _info(fname, expected, actual, flag):
    """
    Convenience function returns nicely formatted error/warning msg.

    """
    format = lambda types: ', '.join([str(t) for t in types])
    expected, actual = format(expected), format(actual)
    msg = "'%s' method " % fname \
          + ("accepts", "returns")[flag] + " (%s), but " % expected\
          + ("was given", "result is")[flag] + " (%s)" % actual
    return msg

from urlparse import urlparse
from cgi import parse_qs
from urllib import unquote

import ast, inspect

def parseURL(url):
    """
    Parses a URL as a tuple (host, path, args) where args is a
    dictionary.
    """


    scheme, host, path, params, query, hash = urlparse(url)
    if not path: path = "/"

    args = parse_qs(query)

    escapedArgs = {}
    for name in args:
        if len(args[name]) == 1:
            escapedArgs[unquote(name)] = unquote(args[name][0])
        else:
            escapedArgs[unquote(name)] = escapedSet = []
            for item in args[name]:
                escapedSet.append(unquote(item))

    return host, path, params, escapedArgs


# TODO: How about for function ?
def getDecoratedMethods(target):
    '''
    Finde the decorators for the object.

    @param target: object.

    @return: dict. ex) {'mom': ['mydeco'], 'get': ['mydeco']} where 'mon'
    and 'get' is the name of function and 'mydeco' is the name of decorator.
    '''
    res = {}
    def visit_FunctionDef(node):
        # We can get also lineno from node
        # node is the definition of function. If node has decorator,
        # node.decorator_list is not nil.
        if len(node.decorator_list):
            # We can get ctx, id, lineno from e
            res[node.name] = [e.id for e in node.decorator_list]

    V = ast.NodeVisitor()
    V.visit_FunctionDef = visit_FunctionDef
    V.visit(compile(inspect.getsource(target), '?', 'exec', ast.PyCF_ONLY_AST))
    return res

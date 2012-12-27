from urlparse import urlparse
from cgi import parse_qs
from urllib import unquote

def parseURL(url):
    """
    Parses a URL into a tuple (host, path, args) where args is a
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

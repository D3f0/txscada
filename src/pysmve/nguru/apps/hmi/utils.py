# Formula related stuff


def generate_tag_context(qs, **aliases):
    """Generate context dict for a table namespace. Eg: DI, AI, EG, etc."""
    result = {}
    for data in qs:
        key = data.pop('tag', None)
        if key:
            context = {}
            for name, value in data.iteritems():
                alias = aliases.get(name, name)
                context[alias] = value
            result[key] = context
    return result


def IF(cond, t, f):
    if cond:
        return t
    else:
        return f


def OR(*args):
    for elem in args:
        if elem:
            return elem


def FILTRAR(filter_func, iterable):
    """Filters but goes through values when dealing with dicts or sublcasses"""
    if isinstance(iterable, dict):
        iterable = iter(iterable.values())
    return filter(filter_func, iterable)



def closest_key(a_string, a_dict):
    '''Returns the closest key in a dictionary to a_string.
    The match is from the begining of the string and scores how
    may chars are the same
    '''
    keys = a_dict.keys()
    closest_key = None
    closest_score = 0

    for key in keys:
        score = 0
        for k_s, k_c in zip(a_string, key):
            if k_s != k_c:
                break
            score += 1
        if score >= closest_score:
            closest_score = score
            closest_key = key
    return closest_key

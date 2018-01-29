

def enum(*sequential, **named):
    # http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
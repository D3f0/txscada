import pyparsing as pp

dotted_notation = pp.Regex(r'[a-zA-Z](\.\d{1,2}(\.\d{1,2})?)?') 
def name_notation_type(tokens):
    name = {
        0 : "area",
        1 : "category",
        2 : "criteria"}[tokens[0].count('.')]
    # assign results name to results - 
    tokens[name] = tokens[0] 
dotted_notation.setParseAction(name_notation_type)

# test each individually
tests = "A A.1 A.2.2".split()
for t in tests:
    print t
    val = dotted_notation.parseString(t)
    print val.dump()
    print val[0], 'is a', val.getName()
    print

# test all at once
tests = "A A.1 A.2.2"
val = pp.OneOrMore(dotted_notation).parseString(tests)
print val.dump()
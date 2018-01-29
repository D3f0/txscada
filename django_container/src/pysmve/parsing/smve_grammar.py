from pyparsing import (
    Word, Regex, Group, oneOf, Forward, CaselessKeyword, Suppress,
    delimitedList, operatorPrecedence, opAssoc, ParseException)


# Variables
variable = Regex(r'(?P<table>[ai|di|sv]{2})\.(?P<tag>[\w\d]+)\.(?P<attr>\w+)')


def var_parse_action(text, index, context):
    return context[0]

variable.setParseAction(var_parse_action)

# Numbers
numeric_literal = Regex(r"\-?\d+(\.\d+)?")


def number_prase_action(text, index, data):
    number = data[0]
    if '.' in number:
        return float(number)
    else:
        return int(number)

numeric_literal.setParseAction(number_prase_action)

EXCL, LPAR, RPAR, COLON, COMMA = map(Suppress, '!():,')

expr = Forward()

# IF CONDITION
COMPARISON_OP = oneOf("< = > >= <= != <>")
condExpr = (expr + COMPARISON_OP + expr) | variable

ifFunc = (CaselessKeyword("si") +
          LPAR +
          Group(condExpr)("condition") +
          COMMA + expr("if_true") +
          COMMA + expr("if_false") + RPAR)

#def ifFunc_parse_action(text, index, context):
#    print "hola"
#    return context
#
#ifFunc.setParseAction(ifFunc_parse_action)


one_op_func = lambda name: (CaselessKeyword(name) + LPAR + expr + RPAR)

int_cast = one_op_func('int')

def int_cast_parse_action(text, index, context):
    return int(context[1])

int_cast.setParseAction(int_cast_parse_action)
float_cast = one_op_func('float')
str_cast = one_op_func('str')

sqrt_func = one_op_func('raiz')


multi_op_func = lambda name: CaselessKeyword(name) + LPAR + delimitedList(expr) + RPAR

# Statistical functions
sumFunc = multi_op_func("sum")
minFunc = multi_op_func("min")
maxFunc = multi_op_func("max")
aveFunc = multi_op_func("ave")

# Logical functions
orFunc = multi_op_func('or')
andFunc = multi_op_func('and')

multOp = oneOf("* /")
addOp = oneOf("+ -")


funcCall = (ifFunc | # If expression
            sumFunc | minFunc | maxFunc | aveFunc | # statisticial functions
            int_cast | str_cast | float_cast | # Casts
            orFunc | andFunc | # Logical
            sqrt_func
            )

operand = funcCall | numeric_literal  | variable

arithExpr = operatorPrecedence(operand,[
                                        (multOp, 2, opAssoc.LEFT),
                                        (addOp, 2, opAssoc.LEFT),
                               ])

def arithExpr_parse_action(text, index, context):
    print "ARIEXPR", context

expr << (arithExpr | funcCall | numeric_literal | variable )


def test_line(line):
    try:
        expr.parseString(line)
    except ParseException as err:
        print err.line
        print " "*(err.column-1) + "^"
        print err

def main():
    ok = 0
    error = []
    with open('formulas.txt') as fp:
        for n, line in enumerate(fp):

            formula = line.strip()
            if not formula:
                continue
            try:
                expr.parseString(formula)
            except ParseException as err:
                print "Number: %d" % n
                print err.line
                print " "*(err.column-1) + "^"
                print err
                return
            try:
                expr.parseString(formula)
                ok += 1
            except:
                print formula
                return
                error.append(formula)
    print "OK: %d (sucess: %.2f)" % (ok, (float(ok) / n) * 100)
    # for i, l in enumerate(error):
    #    print i, l

if __name__ == '__main__':
    #main()
    test_line('int(3)+int(4)')
    test_line('or(0,1,2)')
    test_line('str(aa.bb.cc)')
    test_line('str(si(0>2,aa.bb.cc,4))')
    test_line('RAIZ(ai.E42PA_01.value*ai.E42PA_01.value+ai.E42PR_01.value*ai.E42PR_01.value)*ai.E42PA_01.escala')
    test_line('str(raiz(3)*2)')
    test_line('str(RAIZ(ai.E42PA_01.value*ai.E42PA_01.value+ai.E42PR_01.value*ai.E42PR_01.value)*ai.E42PA_01.escala)')
    #test_integer()
    #test_logic()
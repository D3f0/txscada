import pyparsing
# esto es para acelerar el proceso de parseo
pyparsing.ParserElement.enablePackrat()

from pyparsing import (nestedExpr,
                       Group,
                       Literal,
                       CaselessLiteral,
                       delimitedList,
                       Optional,
                       nums,
                       Combine,
                       oneOf,
                       opAssoc,
                       operatorPrecedence,
                       Suppress,
                       alphanums,
                       alphas,
                       Word,
                       Forward,
                       Regex,
                       )

dot = Literal(".")
underscore = "_"
eg = CaselessLiteral("eg")
si = CaselessLiteral("di")
ai = CaselessLiteral("ai")

lparen = Literal("(")
rparen = Literal(")")

lt = Literal("<")
le = Literal("<=")
gt = Literal(">")
ge = Literal(">=")
eq = Literal("=")

alphanums_extended = alphanums + "-_"

# deficion de numero estilo JSON
number_ext = Combine( Optional('-') +
                    ( '0' | Word('123456789', nums) ) +
                    Optional( '.' + Word(nums) ) +
                    Optional( Word('eE', exact=1) +
                    Word(nums + '+-', nums) ) ).setName("number")

number = Regex(r"\-?\d+(\.\d+)?")

def numberParseAction(s, p, t):
    import ipdb; ipdb.set_trace()

number.setParseAction(numberParseAction)

# queda para definir mas adelante en el codigo
expression = Forward()
function = Forward()
entity = Forward()
lambda_expression = Forward()

# expresiones entre parentesis
enclosed_expression = Group(Suppress(lparen) + expression + Suppress(rparen))

lambda_name = Literal("lambda")
var_name = Word(alphanums_extended)
lambda_vars = delimitedList(var_name)
var_access = Group(var_name +
                   Optional(Suppress(dot) + Word(alphanums_extended)))


term = (enclosed_expression |
        function |
        lambda_expression |
        entity |
        var_access |
        number).setName("term")

lambda_expression << Group(lambda_name +
                           lambda_vars +
                           Suppress(":") +
                           term).setName("lambda expr")

def operations_parse_action(s, p, ts):
    import ipdb; ipdb.set_trace()

expression << operatorPrecedence(term,[
    (oneOf("* /"), 2, opAssoc.LEFT),
    (oneOf("+ -"), 2, opAssoc.LEFT),
    (lt | le | gt | ge | eq, 2, opAssoc.LEFT),
]).setParseAction(operations_parse_action)



#def experssionParseAction(a, b, c):
#    print a, b, c

#expression.setParseAction(experssionParseAction)


function_name = Word(alphas).setName("function_name")
arguments = delimitedList(expression)
function << Group(function_name +
                Suppress(lparen) +
                arguments +
                Suppress(rparen)).setName("function")
#rule = function | expression

entity << Group((si | ai | eg).setName("entity class") +
                Suppress(dot) +
                Word(alphanums_extended).setName("entity name") +
                Suppress(dot) +
                Word(alphanums_extended).setName("entity attribute")
                ).setName("entity")



def test(*args, **kwargs):
    '''Test experssion against a set of formulas stored in
    a plain text file'''
    ok, errors, count = 0, 0, 0
    with open('formulas.txt') as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            count += 1
            try:
                results = expression.parseString(line)
                ok += 1
            except ParseException as err:
                print err.line
                print " "*(err.column-1) + "^"
                print err
                errors += 1

            print line, ">", results
            print "=" * 10
    print "Lines %d OK: %d Errors: %d" % (count, ok, errors)


# Testing
import unittest
class TestFormula(unittest.TestCase):
    def setUp(self):
        self.fp = open('formulas.txt')

    def test_function(self):
        result = expression.parseString('SUM(1,1)')
        self.assertEqual(len(result), 1, "Result evaulation should be only length 1")

    def test_function_1(self):
        result = expression.parseString('2+2+4')

        self.assertEqual(len(result), 1, "Result evaulation should be only length 1")

    def tearDown(self):
        self.fp.close()


def evaluate(parsed, context):

    for expr in parsed:
        if expr[0] == 'SUM':
            pass

def main(argv):
    parsed = expression.parseString(argv[1])
    evaluate(parsed, context={})


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'test':
        test()
    elif len(argv[1:]):
        main(argv)
    else:
        pass

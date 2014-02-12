import pyparsing
# esto es para acelerar el proceso de parseo
pyparsing.ParserElement.enablePackrat()

from pyparsing import nestedExpr
from pyparsing import Group
from pyparsing import Literal
from pyparsing import CaselessLiteral
from pyparsing import delimitedList
from pyparsing import Optional
from pyparsing import nums
from pyparsing import Combine
from pyparsing import oneOf
from pyparsing import opAssoc
from pyparsing import operatorPrecedence
from pyparsing import Suppress
from pyparsing import alphanums
from pyparsing import alphas
from pyparsing import Word
from pyparsing import Forward


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
number = Combine( Optional('-') +
                    ( '0' | Word('123456789', nums) ) +
                    Optional( '.' + Word(nums) ) +
                    Optional( Word('eE', exact=1) +
                    Word(nums + '+-', nums) ) ).setName("number")


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

expression << operatorPrecedence(term,[
    (oneOf("* /"), 2, opAssoc.LEFT),
    (oneOf("+ -"), 2, opAssoc.LEFT),
    (lt | le | gt | ge | eq, 2, opAssoc.LEFT),
])

def experssionParseAction(a, b, c):
    print a, b, c

expression.setParseAction(experssionParseAction)


function_name = Word(alphas).setName("function_name")
arguments = delimitedList(expression)
function << Group(function_name +
                Suppress(lparen) +
                arguments +
                Suppress(rparen)).setName("function")
rule = function | expression

entity << Group((si | ai | eg).setName("entity class") +
                Suppress(dot) +
                Word(alphanums_extended).setName("entity name") +
                Suppress(dot) +
                Word(alphanums_extended).setName("entity attribute")
                ).setName("entity")



def test():
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

if __name__ == '__main__':
    test()
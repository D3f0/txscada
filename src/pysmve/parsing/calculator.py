import sys
import operator
from pyparsing import nums, oneOf, Word
from pyparsing import ParseException
# Map math operations to callable functions within
# the operator module.
op_map = {
    '*': operator.mul,
    '+': operator.add,
    '/': operator.div,
    '-': operator.sub,
    '**': operator.pow
}
# define grammar
MATH_GRAMMAR = Word(nums).setResultsName('first_term') + \
    oneOf('+ - / * **').setResultsName('op') + \
    Word(nums).setResultsName('second_term')


def handle_line(line):
    """
    Parse a newly read line.
    """
    result = MATH_GRAMMAR.parseString(line)
    return op_map[result.op](int(result.first_term),
        int(result.second_term))

while True:
    try:
        print handle_line(raw_input('> '))
    except ParseException, e:
        print >>sys.stderr, \
            "Syntax err at position %d: %s" % (e.col, e.line)


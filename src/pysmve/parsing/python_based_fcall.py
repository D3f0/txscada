# Inspired in
# http://stackoverflow.com/questions/14476208/pyparsing-to-parse-a-python-function-call-in-its-most-general-form
from pyparsing import *
'''
func_call ::= identifier '(' func_arg [',' func_arg]... ')'
func_arg ::= named_arg | arg_expr
named_arg ::= identifier '=' arg_expr
arg_expr ::= identifier | real | integer | dict_literal | list_literal | tuple_literal | func_call
identifier ::= (alpha|'_') (alpha|num|'_')*
alpha ::= some letter 'a'..'z' 'A'..'Z'
num ::= some digit '0'..'9'
'''


cvtInt = lambda toks: int(toks[0])
cvtReal = lambda toks: float(toks[0])
cvtTuple = lambda toks : tuple(toks.asList())
cvtDict = lambda toks: dict(toks.asList())

# define punctuation as suppressed literals
lparen,rparen,lbrack,rbrack,lbrace,rbrace,colon = \
    map(Suppress,"()[]{}:")

integer = Combine(Optional(oneOf("+ -")) + Word(nums))\
    .setName("integer")\
    .setParseAction( cvtInt )
real = Combine(Optional(oneOf("+ -")) + Word(nums) + "." +
               Optional(Word(nums)) +
               Optional(oneOf("e E")+Optional(oneOf("+ -")) +Word(nums)))\
    .setName("real")\
    .setParseAction( cvtReal )
tupleStr = Forward()
listStr = Forward()
dictStr = Forward()

listItem = real|integer|quotedString.setParseAction(removeQuotes)| \
            Group(listStr) | tupleStr | dictStr

tupleStr << ( Suppress("(") + Optional(delimitedList(listItem)) +
            Optional(Suppress(",")) + Suppress(")") )
tupleStr.setParseAction( cvtTuple )

listStr << (lbrack + Optional(delimitedList(listItem) +
            Optional(Suppress(","))) + rbrack)

dictEntry = Group( listItem + colon + listItem )
dictStr << (lbrace + Optional(delimitedList(dictEntry) + \
    Optional(Suppress(","))) + rbrace)
dictStr.setParseAction( cvtDict )


identifier = Word(alphas+'_', alphanums+'_')


# define a placeholder for func_call - we don't have it yet, but we need it now
func_call = Forward()

# Arithmetics (from http://pyparsing.wikispaces.com/file/view/simpleArith.py)
expop = Literal('^')
signop = oneOf('+ -')
multop = oneOf('* /')
plusop = oneOf('+ -')
factop = Literal('!')

operand = identifier | real | integer | func_call

arithmetic_expr = operatorPrecedence( operand,
    [("!", 1, opAssoc.LEFT),
     ("^", 2, opAssoc.RIGHT),
     (signop, 1, opAssoc.RIGHT),
     (multop, 2, opAssoc.LEFT),
     (plusop, 2, opAssoc.LEFT),]
    )


#arg_expr = identifier | real | integer | dictStr | listStr | tupleStr | func_call
arg_expr = identifier | real | integer | func_call

named_arg = identifier + '=' + arg_expr

# to define func_arg, must first see if it is a named_arg
# why do you think this is?
func_arg = named_arg | arg_expr | arithmetic_expr

#deref_list = '*' + (identifier | list_literal | tuple_literal)
#deref_dict = '**' + (identifier | dict_literal)

#arg_expr = identifier | real | integer | dict_literal | list_literal | tuple_literal | func_call | deref_list | deref_dict

# now define func_call using '<<' instead of '=', to "inject" the definition
# into the previously declared Forward
#
# Group each arg to keep its set of tokens separate, otherwise you just get one
# continuous list of parsed strings, which is almost as worthless the original
# string
func_call << identifier + lparen + delimitedList(func_arg) + rparen


grammar = (arithmetic_expr | func_call)

def test():
    print grammar.parseString('3+4')
    print grammar.parseString('sin(3+4)')



test()
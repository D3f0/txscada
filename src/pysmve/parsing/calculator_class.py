from pyparsing import Word, nums, Literal, ParseException
from string import lowercase


'str(ai.E4CVV_01.value*ai.E4CVV_01.escala)'

class Calculator(object):
    nonzero = ''.join([str(i) for i in range(1, 10)])
    integer = Word(nonzero, nums)
    varname = Word(lowercase)
    equals = Literal('=').suppress()
    operator = Word('+-*/', exact=1)
    operand = integer ^ varname
    unaryoperation = operand
    binaryoperation = operand + operator + operand
    operation = unaryoperation ^ binaryoperation
    expression = varname + equals + operation

    def __init__(self):
        self._state = dict()

    def execute_command(self, cmd):
        try:
            parts = self._parse_command(cmd)
        except ParseException, err:
            print 'Exception while parsing command: %s' % err
            return

        if len(parts) == 2:
            self._do_basic_assignment(parts)
        else:
            self._do_calculated_assignment(parts)

    def dump_state(self):
        print self._state

    def _parse_command(self, cmd):
        return self.expression.parseString(cmd)

    def _do_basic_assignment(self, parts):
        value = self._get_value(parts[1])
        if value is None:
            print 'Unable to execute command'
            return
        self._state[parts[0]] = value

    def _get_value(self, s):
        value = None

        try:
            value = int(s)
        except ValueError:
            pass

        if value is None:
            try:
                value = self._state[s]
            except KeyError:
                print 'Unknown variable: %s' % s
                return None

        return value

    def _do_calculated_assignment(self, parts):
        op1 = parts[1]
        op2 = parts[3]
        operator = parts[2]

        op1 = self._get_value(op1)
        op2 = self._get_value(op2)

        if op1 is None or op2 is None:
            print 'Unable to execute command'
            return

        funcs = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
        }

        self._state[parts[0]] = funcs[operator](op1, op2)

def main():
    print 'Press ^C to quit'
    print

    calc = Calculator()

    while True:
        cmd = raw_input('> ')
        calc.execute_command(cmd)
        calc.dump_state()

if __name__ == '__main__':
    main()
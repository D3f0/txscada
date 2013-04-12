from pyparsing import Word, OneOrMore, ZeroOrMore
from string import lowercase

word = Word(lowercase)

print word.parseString('hello')

sentnce = OneOrMore(word)


print sentnce.parseString('hello world')

two_words = word + word

print two_words.parseString('cosa loca')

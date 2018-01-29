# [String.format()]()
## JavaScript sprintf/console.log()/String.Format() inspired formatting library
## 997 bytes minified, 576 bytes gzipped.

String-format is a micro library that provides a very simple but very useful format() method to your string literals allowing you to access sprintf like formatting on the fly, e.g.

```js
'This is a string %s'.format('literal') // 'This is a string literal'
```

This product is the evolution of a tool that I've copied from project to project in one form or another over several years. In
true coder form, it's updated, unit tested, and documented on github right now because I'm procrastinating another project.

## Syntax

- `%s` : substitute a string
  - `%Ds` : limit the substituted string to 2 characters
  - `%D.Xs` : substr starting at index D and X characters long
- `%f` : substitute a floating point number, no leading zero
  - `%0f` : floating point with leading zero
  - `%.Df` : fixed to D decimal places
  - `%0.Df` : fixed to D decimal places with leading zero
  - `%,Df` : Using a comma will add a comma separator every 3 digits
- `%d` or `%i` : substitute an integer (zero decimal places)
  - `%,d` : add comma separator every 3 digits
- `%%` : literal % sign

## Examples

```javascript
'Github is %s'.format('awesome');                  // "Github is awesome"
'One answer may be %i'.format(42);                 // "One answer may be 42"
'Another answer may be %.5f'.format(Math.PI);      // "Another answer may be 3.14159"
'%.5f is not equal to %.5f'.format(22/7, Math.PI); // "3.14286 is not equal to 3.14159"
'PI minus 3 is %0.5f'.format(Math.PI - 3);         // "PI minus 3 is 0.14159"
'%,d is a really big number'.format(299792458);    // "299,792,458 is a really big number"
'%0,2f is a smaller number'.format(12021.12);      // "12,021.12 is a smaller number"
```

The format() method is on every string, not just literal strings.

```javascript
var header = 'Welcome, %s';
header.format("Bob")          // "Welcome, Bob"
```

## License

MIT/BSD License

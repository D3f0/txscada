/*global describe,beforeEach,it,expect,PF*/

describe("String format", function() {
  "use strict";

  beforeEach(function() {
  });

  describe('Format parser',function(){
    it("Should parse double percents", function() {
      var parts = PF('%%f');
      expect(parts.length).toEqual(1);
      expect(parts[0].h).toBeUndefined();
      expect(parts[0].t).toEqual('%');
    });

    it("Should parse multiple double percents mixed", function() {
      var parts = PF('%%a%bc%%');
      expect(parts.length).toEqual(3);
      expect(parts[0].h).toBeUndefined();
      expect(parts[0].t).toEqual('%');
      expect(parts[1].h[0]).toBeUndefined();
      expect(parts[1].h[1]).toBeUndefined();
      expect(parts[1].t).toEqual('b');
      expect(parts[2].h).toBeUndefined();
      expect(parts[2].t).toEqual('%');
    });

    it("Should parse type", function() {
      var parts = PF('%s');
      expect(parts.length).toEqual(1);
      expect(parts[0].h[0]).toBeUndefined();
      expect(parts[0].h[1]).toBeUndefined();
      expect(parts[0].t).toEqual('s');
    });

    it("Should parse major precision", function() {
      var parts = PF('%2.f');
      expect(parts.length).toEqual(1);
      expect(parts[0].h[0]).toEqual(2);
      expect(parts[0].h[1]).toBeUndefined();
      expect(parts[0].t).toEqual('f');

      parts = PF('%2f');
      expect(parts.length).toEqual(1);
      expect(parts[0].h[0]).toEqual(2);
      expect(parts[0].h[1]).toBeUndefined();
      expect(parts[0].t).toEqual('f');

      parts = PF('%2.0f');
      expect(parts.length).toEqual(1);
      expect(parts[0].h[0]).toEqual(2);
      expect(parts[0].h[1]).toEqual(0);
      expect(parts[0].t).toEqual('f');
    });

    it("Should parse minor precision", function() {
      var parts = PF('%.5f');
      expect(parts.length).toEqual(1);
      expect(parts[0].h[0]).toBeUndefined();
      expect(parts[0].h[1]).toEqual(5);
      expect(parts[0].t).toEqual('f');

      parts = PF('%0.5f');
      expect(parts.length).toEqual(1);
      expect(parts[0].h[0]).toEqual(0);
      expect(parts[0].h[1]).toEqual(5);
      expect(parts[0].t).toEqual('f');
    });

    it("Should parse full format options", function() {
      var parts = PF('%2.8d');
      expect(parts.length).toEqual(1);
      expect(parts[0].h[0]).toEqual(2);
      expect(parts[0].h[1]).toEqual(8);
      expect(parts[0].t).toEqual('d');
    });

    it("Should parse multiple format options", function() {
      var parts = PF('%2.8d unparsed %% %%f unparsed %1.9s');
      expect(parts.length).toEqual(4);
      expect(parts[0].h[0]).toEqual(2);
      expect(parts[0].h[1]).toEqual(8);
      expect(parts[0].t).toEqual('d');
      expect(parts[1].h).toBeUndefined();
      expect(parts[1].t).toEqual('%');
      expect(parts[2].h).toBeUndefined();
      expect(parts[2].t).toEqual('%');
      expect(parts[3].h[0]).toEqual(1);
      expect(parts[3].h[1]).toEqual(9);
      expect(parts[3].t).toEqual('s');
    });
  });

  it("Should format string values", function() {
    expect('a%sc'.format('b')).toEqual('abc');
    expect('a%2sc'.format('abc')).toEqual('aabc');
    expect('a%1.2sc'.format('abcd')).toEqual('abcc');
  });

  it("Should format mixed values", function() {
    expect('%%a%sc%%'.format('b')).toEqual('%abc%');
  });

  it("Should format float values without precision", function() {
    expect('%f'.format(2.4242)).toEqual('2.4242');
    expect('%f'.format(2.424200)).toEqual('2.4242');
    expect('%f'.format(.4)).toEqual('.4');
    expect('%f'.format(-.4)).toEqual('-.4');
    expect('%f'.format(-12.4)).toEqual('-12.4');
  });

  it("Should format float values with major precision 0", function() {
    expect('%0.f'.format(.4)).toEqual('0.4');
    expect('%0.f'.format(-12.4)).toEqual('-12.4');
    expect('%0.f'.format(-.4)).toEqual('-0.4');
  });

  it("Should format float values with minor precision", function() {
    expect('%.2f'.format(1234.1234)).toEqual('1234.12');
    expect('%.2f'.format(1234.1255)).toEqual('1234.13');
    expect('%.0f'.format(1234.1234)).toEqual('1234');
    expect('%.5f'.format(1234.1234)).toEqual('1234.12340');
  });

  it("Should fail gracefully on unmatched args", function() {
    expect('%i%0.2f%s%i'.format()).toEqual('00.000');
  });

  it("Should format int values", function() {
    expect('%i'.format(1234)).toEqual('1234');
    expect('%i'.format(1234.1234)).toEqual('1234');
    expect('%d'.format(1234.1255)).toEqual('1234');
  });

  it("Should format values with commas", function() {
    expect('%,i'.format(1234567)).toEqual('1,234,567');
    expect('%,i'.format(1234.1234)).toEqual('1,234');
    expect('%,d'.format(1234.1255)).toEqual('1,234');
    expect('%,f'.format(1234.1255)).toEqual('1,234.1255');
    expect('%0,2f'.format(0.1255)).toEqual('0.13');
    expect('%0,2f'.format(1234.1255)).toEqual('1,234.13');
  });


});

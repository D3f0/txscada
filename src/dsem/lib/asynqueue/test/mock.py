# Twisted Goodies:
# Miscellaneous add-ons and improvements to the separately maintained and
# licensed Twisted (TM) asynchronous framework. Permission to use the name was
# graciously granted by Twisted Matrix Laboratories, http://twistedmatrix.com.
#
# Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Mock object support for twisted_goodies unit tests
"""

import os, copy
from twisted.internet import defer, reactor
from twisted.trial import unittest


DELAY = 0.05

def deferToLater(*args, **kw):
    delay = kw.pop('delay', DELAY)
    if args:
        arg = args[0]
    else:
        arg = None
    d = defer.Deferred()
    if callable(arg):
        d.addCallback(lambda _: arg(*args[1:], **kw))
        reactor.callLater(delay, d.callback, None)
    else:
        reactor.callLater(delay, d.callback, arg)
    return d

def fireLater(d, value=None, delay=None):
    """
    Fires the supplied deferred I{d} with I{value}, or C{None} if no value
    supplied, after the standard or specified I{delay}.
    """
    if delay is None:
        delay = DELAY
    reactor.callLater(delay, d.callback, value)


class Mock(object):
    """
    I am the foundation for all mock objects in a test suite. Subclass me to
    make your mock object, and calls to its methods will be logged for test and
    debugging purposes.

    This class was written by Edwin A. Suominen, and dedicated to the Public
    Domain, in 2007.
    """
    calls = []
    delay = 0.05
    
    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if name in object.__getattribute__(self, '__class__').__dict__:
            if callable(value):
                value = object.__getattribute__(self, 'decorate')(value)
        return value

    @classmethod
    def clearCalls(cls):
        while cls.calls:
            cls.calls.pop()
    
    @staticmethod
    def verbose(level=1):
        verbosity = os.environ.get('VERBOSE', 0)
        return int(verbosity) >= level

    def decorate(self, f):
        """
        Decorate your function with this method and calls to it will be
        recorded and possibly printed, depending on the value of the
        VERBOSE environment variable.
        """
        def conform(arg):
            if isinstance(arg, str):
                return "'%s'" % arg
            if isinstance(arg, (float, int, long)):
                return str(arg)
            if hasattr(arg, '__name__'):
                return arg.__name__
            return repr(arg)
        
        def wrapper(*args, **kw):
            def isPrintable(funcName):
                if not self.verbose(2):
                    return False
                if self.verbose(3):
                    return True
                return not funcName.split(".")[-1].startswith("_")
            
            def gotRealResult(realResult, msg):
                print "%s\n  -//-> %s" % (msg, conform(realResult))
                return realResult

            if hasattr(f, "im_class"):
                funcName = f.im_class.__name__ + "." + f.__name__
                funcName = funcName.replace("Mock_", "")
            else:
                funcName = f.__name__
            argList = []
            for arg in args:
                argList.append(conform(arg))
            for name, value in kw.iteritems():
                argList.append("%s=%s" % (name, conform(value)))
            argString = ", ".join(argList)
            calls = object.__getattribute__(self, 'calls')
            calls.append([funcName, args, kw, None])
            N = len(calls)
            result = f(*args, **kw)
            calls[N-1][-1] = result
            if isPrintable(funcName):
                msg = "\n%3d: %s(%s)" % (N, funcName, argString)
                if isinstance(result, defer.Deferred):
                    result.addBoth(gotRealResult, msg)
            return result
        wrapper.__name__ = f.__name__
        return wrapper

    def deferToCalls(self):
        def gotResult(result, call):
            call[-1] = result
            return result
        
        dList = []
        for k, call in enumerate(self.calls):
            result = call[-1]
            if isinstance(result, defer.Deferred):
                result.addCallback(gotResult, call)
                dList.append(result)
        return defer.DeferredList(dList).addCallback(lambda _: self.calls)

    def deferToLater(self, *args, **kw):
        kw['delay'] = self.delay
        return deferToLater(*args, **kw)
    
    def fireLater(self, *args, **kw):
        kw['delay'] = self.delay
        return fireLater(*args, **kw)


class TestCase(unittest.TestCase):
    """
    I am a somewhat more featureful version of Twisted Trial's C{TestCase}.
    """
    def failUnlessElementsEqual(self, a, b, msg=None):
        args = []
        for x in (a, b):
            args.append(list(x))
            args[-1].sort()
        if msg:
            args.append(msg)
        self.failUnlessEqual(*args)

    @defer.deferredGenerator
    def caserator(self, method, expectations, cases, comparator=None):
        if not expectations or not isinstance(expectations, (list, tuple)):
            expectations = [expectations] * len(cases)
        if not callable(comparator):
            comparator = self.failUnlessEqual
        k = 0
        for expectation in expectations:
            args = cases[k]
            if k+1 < len(cases):
                nextThing = cases[k+1]
            else:
                nextThing = None
            if isinstance(nextThing, dict):
                kw = nextThing
                k += 2
            else:
                kw = {}
                k += 1
            wfd = defer.waitForDeferred(method(*args, **kw))
            yield wfd
            x, y = wfd.getResult(), expectation
            comparator(x, y)

    def nextCall(self, *args, **kw):
        """
        Initialize by calling with a list of calls that were made, as a
        (single) argument.

        With a string as the first (possibly only) argument, runs through the
        expected call list until finding the expected call. If the call is
        found, the args and keywords of the call will be checked against any
        expected args supplied as tuple second arg, and any expected keywords
        supplied as a dict third argument.

        If the I{mustNot} keyword is set C{True}, a call supplied as a first
        argument must B{NOT} be found. Other arguments are ignored.
        """
        def formatArgs(args):
            return ", ".join([str(x) for x in args])

        def formatKw(kw):
            return ", ".join(
                ["%s=%s" % tuple([str(x) for x in y])
                 for y in kw.iteritems()])

        if isinstance(args[0], (list, tuple)):
            self._calls = copy.copy(args[0])
            return
        expectedSuffix = args[0]
        mustNot = kw.get('mustNot', False)
        if kw.get('compareElements', False):
            comparator = self.failUnlessElementsEqual
        else:
            comparator = self.failUnlessEqual
        
        while self._calls:
            thisCall = self._calls.pop(0)
            if thisCall[0].endswith(expectedSuffix):
                if mustNot:
                    self.fail(
                        "Call ending with '%s' should not have been made" \
                        % expectedSuffix)
                break
        else:
            if mustNot:
                return
            self.fail(
                "Expected call ending with '%s' not made" % expectedSuffix)

        if len(args) > 1:
            expectedArgs = args[1]
            msg = "Args '%s' for call '%s' expected to be '%s'" % \
                  (formatArgs(thisCall[1]),
                   thisCall[0], formatArgs(expectedArgs))
            comparator(thisCall[1], expectedArgs, msg)
        if len(args) > 2:
            expectedKw = args[2]
            msg = "Keyword combo '%s' for call '%s' expected to be '%s'" % \
                  (formatKw(thisCall[2]), thisCall[1], formatKw(expectedKw))
            comparator(thisCall[2], expectedKw, msg)


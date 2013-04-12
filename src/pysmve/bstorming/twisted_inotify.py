import os
from twisted.internet import inotify, reactor
from twisted.python import filepath


def notify(ignored, filepath, mask):
   """
   For historical reasons, an opaque handle is passed as first
   parameter. This object should never be used.

   @param filepath: FilePath on which the event happened.
   @param mask: inotify event as hexadecimal masks
   """
   print mask
   print "event %s on %s" % (
       ', '.join(inotify.humanReadableMask(mask)), filepath)

notifier = inotify.INotify()
notifier.startReading()
notifier.watch(filepath.FilePath(os.getcwd()), callbacks=[notify])
reactor.run()
from django.db import transaction
from base import MaraClientProtocol


class MaraClientDBUpdater(MaraClientProtocol):

    '''
    This protocols saves data from scans into the
    database using Peewee ORM. This may change
    in the future.
    '''
    #@transaction.commit_manually
    def saveInDatabase(self):
        self.factory.comaster.process_frame(self.input)
        #transaction.commit()
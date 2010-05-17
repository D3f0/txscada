# sAsync:
# An enhancement to the SQLAlchemy package that provides persistent
# dictionaries, text indexing and searching, and an access broker for
# conveniently managing database access, table setup, and
# transactions. Everything can be run in an asynchronous fashion using the
# Twisted framework and its deferred processing capabilities.
#
# Copyright (C) 2006 by Edwin A. Suominen, http://www.eepatents.com
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
Text indexing and searching (TODO)

"""

# Imports
from twisted.internet import defer
import sqlalchemy as SA
from sasync.database import AccessBroker

# Config
TRUNCATED_WORD_LENGTH   = 20


class Records:
    """
    Abstract base for record keeping classes
    """
    pass


class DatabaseRecords(Records):
    """
    I keep text records in the database of my searcher parent 
    """
    def startup(self, parent):
        self.parent = parent
        return parent.table(
            'records',
            SA.Column('doc_id', SA.Integer, index="section"),
            SA.Column('section_id', SA.Integer, index="section"),
            SA.Column('text', SA.String, nullable=False)
            )

    def addRecord(self, record, document=None, section=None):
        """
        Adds a I{record} supplied as a Python object with a unique integer
        I{document} identifier. The Python object must have a string
        representation that provides its text content. You can supply a unique
        integer I{section} as a keyword.

        @return: A C{Deferred} to a list of unique words extracted from the
            file's plain text content for indexing.
            
        """
        if not instance(document, int):
            raise ValueError("You must supply an integer document ID")
        pass

    def getRecord(self, document, section=None, first=None, last=None):
        """
        Returns a C{Deferred} to the text content of the I{document},
        optionally limited to a particular I{section}.

        The text content to be returned can be restricted to a block of text
        starting at a I{first} word and ending at a I{last} word, with the word
        positions supplied as integer keywords.
        """
        pass


class FileRecords(Records):
    """
    I use existing files as text records
    """
    def startup(self, parent):
        self.parent = parent
        return defer.succeed(None)

    def addRecord(self, record, document=None, section=None):
        """
        Adds a I{record} supplied as the valid path of a file. A hash of the
        unique file path is used as the document identifier and only the
        default section is used. Thus any I{document} or I{section} keyword IDs
        supplied are ignored.

        @return: A C{Deferred} to a list of unique words extracted from the
            file's plain text content for indexing.
            
        """
        pass

    def getRecord(self, document, section=None, first=None, last=None):
        """
        Returns a C{Deferred} to the text content of the I{document} supplied
        as the valid path of a file that has been added as a record. Any
        I{section} keyword supplied is ignored because different sections of
        files are not recognized.

        The text content to be returned can be restricted to a block of text
        starting at a I{first} word and ending at a I{last} word, with the word
        positions supplied as integer keywords.
        """
        if not instance(document, int):
            raise ValueError("You must supply an integer document ID")
        pass


class Search(AccessBroker):
    """
    I provide an interface for indexing terms of new records and searching for
    text contained within records already indexed.

    I am instantiated with a reference to whatever subclass of L{Records} I
    should instantiate to extract text from objects presented for indexing and
    convert word positions of search results back into the text of the original
    objects.
    """
    def __init__(self, recordsClass):
        self.keeper = recordsClass()
    
    def userStartup(self):
        AccessBroker.__init__(self, twisted=True)
        d1 = self.table(
            'words',
            SA.Column('id', SA.Integer, index="word"),
            SA.Column('word',
                   SA.String(TRUNCATED_WORD_LENGTH),
                   primary_key=True)
            )
        d2 = self.table(
            'usage',
            SA.Column('word_id', Integer, primary_key=True, index="scope"),
            Column('doc_id', Integer, index="scope"),
            Column('section_id', Integer, index="scope"),
            Column('position', Integer, nullable=False)
            )
        self._ready = True
        d3 = self.keeper.startup(self)
        return defer.DeferredList([d1,d2,d3])

    def busy(self, *args):
        """
        Indicates that indexing is in progress, which forces calls to my
        L{search} method to queue up until I{ready} status resumes.
        """
        self._ready = False

    def ready(self, *args):
        """
        Indicates that no indexing is in progress, which permits calls to my
        L{search} method to start working on queries immediately
        """
        self._ready = True

    def index(self, record, document=None, section=None):
        """
        Indexes the text content of the supplied I{record} under the supplied
        I{document} and I{section} identifiers, which must be integers if
        specified.

        Returns a C{Deferred} that fires with no argument when the indexing is
        done.

        If no document is specified, the text is considered as being at the end
        of whatever has already been indexed for a default document with the
        identifier of zero. Likewise, every document (including the default)
        has a default section, also with C{ID=0}, for indexing and searching of
        records with no section specified.
        """
        return defer.succeed(None)

    def drop(self, document, section=None):
        """
        Drops the index entries for the supplied I{document} and optionally
        supplied I{section} identifies, which must be integers.

        Returns a C{Deferred} that fires with no argument when the index update
        is done.

        If no section is specified, the index entries for the default document
        will be dropped.
        """
        return defer.succeed(None)
    
    def search(self, query, scope=None):
        """
        Searches the record of the documents with IDs in the supplied I{scope}
        sequence for matches with the supplied query. Items of B{all}
        dictionaries are searched if no restriction on search scope is defined.

        Returns a C{Deferred} that fires with the results of the search when it
        is done. The results are passed to the callback as a list of tuples
        C{(first, last, words, document, section)} that specify matching blocks
        of text from each matching record. The tuple elements are, in order:

            - B{first}: An integer specifying the position of the C{first} word
              in the matching text block within the specified section of the
              specified document.

            - B{last}: An integer specifying the position of the C{last} word
              in the matching text block within the specified section of the
              specified document.

            - B{words}: A list containing integer positions of words that
              triggered the match.

            - B{document}: An integer specifying the document in which the text
              block was found.
            
            - B{section}: An integer specifying the section of the document in
              which the text block was found.

        @todo: Initially the query just contains terms that must all be present
            in the item's text value, I{i.e.}, logical AND. Expand this method
            to parse the query for proximity operators etc.

        """
        results = []
        return defer.succeed(results)

    def record(self, document, section=None, first=None, last=None):
        """
        Returns a C{Deferred} to the text content of the record for the
        specified I{document}, optionally limited to a particular I{section}.

        The text content to be returned can be restricted to a block of text
        starting at a I{first} word and ending at a I{last} word, with the word
        positions supplied as integer keywords.
        """
        pass

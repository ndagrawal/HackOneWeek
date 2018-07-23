# -*- encoding: utf-8 -*-
"""
Tokenizer for IcM incident text contained in IcM and emails. It is
derived from
http://www.nltk.org/_modules/nltk/tokenize/casual.html#TweetTokenizer.

The basic logic is this:

1. The tuple regex_strings defines a list of regular expression
   strings.

2. The regex_strings strings are put, in order, into a compiled
   regular expression object called word_re.

3. The tokenization is done by word_re.findall(s), where s is the
   user-supplied string, inside the tokenize() method of the class
   Tokenizer.

4. When instantiating Tokenizer objects, there is a single option:
   preserve_case.  By default, it is set to True. If it is set to
   False, then the tokenizer will downcase everything except for
   emoticons.

"""

######################################################################

from __future__ import unicode_literals
import re
#from nltk.compat import htmlentitydefs, int2byte, unichr
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from bs4 import BeautifulSoup

######################################################################
# The following strings are components in the regular expression
# that is used for tokenizing. It's important that phone_number
# appears first in the final regex (since it can contain whitespace).
# It also could matter that tags comes after emoticons, due to the
# possibility of having text like
#
#     <:| and some text >:)
#
# Most importantly, the final element should always be last, since it
# does a last ditch whitespace-based tokenization of whatever is left.

# ToDo: Update with http://en.wikipedia.org/wiki/List_of_emoticons ?

# This particular element is used in a couple ways, so we define it
# with a name:
EMOTICONS = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
      |
      <3                         # heart
    )"""

# URL pattern due to John Gruber, modified by Tom Winzig. See
# https://gist.github.com/winzig/8894715

URLS = r"""                             # Capture 1: entire matched URL
  (?:
  https?:                               # URL protocol and colon
    (?:
      /{1,3}                            # 1-3 slashes
      |                                 #   or
      [a-z0-9%]                         # Single letter or digit or '%'
                                        # (Trying not to match e.g. "URI::Escape")
    )
    |                                   #   or
                                        # looks like domain name followed by a slash:
    [a-z0-9.\-]+[.]
    (?:[a-z]{2,13})
    /
  )
  (?:                                   # One or more:
    [^\s()<>{}\[\]]+                    # Run of non-space, non-()<>{}[]
    |                                   #   or
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\)  # balanced parens, one level deep: (...(...)...)
    |
    \([^\s]+?\)                         # balanced parens, non-recursive: (...)
  )+
  (?:                                   # End with:
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\)  # balanced parens, one level deep: (...(...)...)
    |
    \([^\s]+?\)                         # balanced parens, non-recursive: (...)
    |                                   #   or
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]      # not a space or one of these punct chars
  )
  |                                     # OR, the following to match naked domains:
  (?:
          (?<!@)                        # not preceded by a @, avoid matching foo@_gmail.com_
    [a-z0-9]+
    (?:[.\-][a-z0-9]+)*
    [.]
    (?:[a-z]{2,13})
    \b
    /?
    (?!@)                               # not succeeded by a @,
                                        # avoid matching "foo.na" in "foo.na@example.com"
  )
"""

# The components of the tokenizer:
IncidentRegexps = [
    ("url", URLS),
    # Phone numbers:
    ("phone-no", r"""
        (?:
          (?:            # (international)
            \+?[01]
            [\-\s.]*
          )?
          (?:            # (area code)
            [\(]?
            \d{3}
            [\-\s.\)]*
          )?
          \d{3}          # exchange
          [\-\s.]*
          \d{4}          # base
        )""")
    ,
    # ASCII Emoticons
    ("emoticon", EMOTICONS)
    ,
    # HTML tags:
    ("html-tag", r"""<[^>\s]+>""")
    ,
    # ASCII Arrows
    ("ascii-arrow", r"""[\-]+>|<[\-]+""")
    ,
    # IP Addresses
    ("ipv4-address", r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
    ,
    # GUID pattern
    # TODO : RITWIK i have commented this out because this was not working....... sre_constants.error: bad escape \h at position
    #("guid", r'\h{8}\.\h{4}.\h{4}.\h{4}.\h{12}')
    #,
    # email addresses
    ("email", r"""[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]""")
    ,
    # Remaining word types:
    ("word", r"""
        (?:[^\W\d_](?:[^\W\d_]|['\-_])+[^\W\d_]) # Words with apostrophes or dashes.
        |
        (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
        |
        (?:[\w_]+)                     # Words without apostrophes or dashes.
        |
        (?:\.(?:\s*\.){1,})            # Ellipsis dots.
        |
        (?:\S)                         # Everything else that isn't whitespace.
        """)
]

######################################################################
# This is the core tokenizing regex:

WORD_RE = re.compile(r"""(%s)""" % "|".join([regex for (label, regex) in IncidentRegexps]),
                     re.VERBOSE | re.I | re.UNICODE)

# WORD_RE performs poorly on these patterns:
HANG_RE = re.compile(r'([^a-zA-Z0-9])\1{3,}')

# The emoticon string gets its own regex so that we can preserve case for
# them as needed:
EMOTICON_RE = re.compile(EMOTICONS, re.VERBOSE | re.I | re.UNICODE)

# These are for regularizing HTML entities to Unicode:
ENT_RE = re.compile(r'&(#?(x?))([^&;\s]+);')

URL_RE = re.compile(URLS, re.VERBOSE | re.I | re.UNICODE)


######################################################################
# Functions for converting html entities
######################################################################

def _str_to_unicode(text, encoding=None, errors='strict'):
    if encoding is None:
        encoding = 'utf-8'
    if isinstance(text, bytes):
        return text.decode(encoding, errors)
    return text


def _replace_html_entities(text, keep=(), remove_illegal=True, encoding='utf-8'):
    """
    Remove entities from text by converting them to their
    corresponding unicode character.

    :param text: a unicode string or a byte string encoded in the given
    `encoding` (which defaults to 'utf-8').

    :param list keep:  list of entity names which should not be replaced.\
    This supports both numeric entities (``&#nnnn;`` and ``&#hhhh;``)
    and named entities (such as ``&nbsp;`` or ``&gt;``).

    :param bool remove_illegal: If `True`, entities that can't be converted are\
    removed. Otherwise, entities that can't be converted are kept "as
    is".

    :returns: A unicode string with the entities removed.

    See https://github.com/scrapy/w3lib/blob/master/w3lib/html.py

        >>> from nltk.tokenize.casual import _replace_html_entities
        >>> _replace_html_entities(b'Price: &pound;100')
        'Price: \\xa3100'
        >>> print(_replace_html_entities(b'Price: &pound;100'))
        Price: £100
        >>>
    """

    def _convert_entity(match):
        entity_body = match.group(3)
        if match.group(1):
            try:
                if match.group(2):
                    number = int(entity_body, 16)
                else:
                    number = int(entity_body, 10)
                # Numeric character references in the 80-9F range are typically
                # interpreted by browsers as representing the characters mapped
                # to bytes 80-9F in the Windows-1252 encoding. For more info
                # see: http://en.wikipedia.org/wiki/Character_encodings_in_HTML
                if 0x80 <= number <= 0x9f:
                    return int2byte(number).decode('cp1252')
            except ValueError:
                number = None
        else:
            if entity_body in keep:
                return match.group(0)
            else:
                number = htmlentitydefs.name2codepoint.get(entity_body)
        if number is not None:
            try:
                return unichr(number)
            except ValueError:
                pass

        return "" if remove_illegal else match.group(0)

    return ENT_RE.sub(_convert_entity, _str_to_unicode(text, encoding))


######################################################################
class IncidentTokenizer:
    r"""
    Cleaner for incident text.

        >>> from IncidentTextTagger.tokenizer import IncidentTextTokenizer
        >>> tknzr = IncidentTextTokenizer()
        >>> s0 = "This is a cooool #dummysmiley: :-) :-P <3 and some arrows < > -> <--"
        >>> tknzr.tokenize(s0)
        ['This', 'is', 'a', 'cooool', '#dummysmiley', ':', ':-)', ':-P', '<3', 'and', 'some', 'arrows', '<', '>', '->', '<--']

    Examples using `strip_handles` and `reduce_len parameters`:

        >>> tknzr = IncidentTextTokenizer(strip_handles=True, reduce_len=True)
        >>> s1 = '@remy: This is waaaaayyyy too much for you!!!!!!'
        >>> tknzr.tokenize(s1)
        [':', 'This', 'is', 'waaayyy', 'too', 'much', 'for', 'you', '!', '!', '!']
    """

    def __init__(self, preserve_case=False,
                 reduce_len=False,
                 remove_stopwords=True,
                 stem_words=True,
                 keep_onlyalphanumeric=False,
                 remove_urls=True):
        self.preserve_case = preserve_case
        self.reduce_len = reduce_len
        self.remove_stopwords = remove_stopwords
        self.stem_words = stem_words
        self.stemmer = SnowballStemmer('english')
        self.stops = set(stopwords.words("english"))
        self.keep_onlyalphanumeric = keep_onlyalphanumeric
        self.remove_urls = remove_urls

    def tokenize(self, text):
        """
        :param text: str
        :rtype: list(str)
        :return: a tokenized list of strings; concatenating this list returns\
        the original string if `preserve_case=False`
        """
        text = str(text)
        # Remove Html tags
        text = BeautifulSoup(text, "lxml").get_text(' ')
        text = re.sub('<[^>\s]+>', ' ', text)
        ## Remove other xml tags in second pass
        text = BeautifulSoup(text, "lxml").text
        #if self.remove_urls:
            #text = URL_RE.sub(' ', text)

            # Remove email address
        text = re.sub('[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]', '', text)

        # Remove Ip address
        text = re.sub('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', '',
                      text)

        # Fix HTML character entities:
        #text = _replace_html_entities(text)
        # Remove xml tags
        text = re.sub('<[^>]*>', ' ', text)

        # Normalize word lengthening
        if self.reduce_len:
            text = reduce_lengthening(text)
        # Shorten problematic sequences of characters
        text = HANG_RE.sub(r'\1\1\1', text)

        # Remove token with more than 100 characters
        text = re.sub('([A-Za-z0-9+/=]{100,})|(\s+)', ' ', text)

        # keep only alpha numeric
        if (self.keep_onlyalphanumeric):
            text = re.sub('[\W_]+', ' ', text)

        # Possibly alter the case
        if not self.preserve_case:
            text = text.lower()

        # Tokenize string
        words = text.split()

        # Remove stop words
        if self.remove_stopwords:
            words = [w for w in words if not w in self.stops]

        # stem_words
        if self.stem_words:
            words = [self.stemmer.stem(word) for word in words]

        return words


######################################################################
# Normalization Functions
######################################################################

def reduce_lengthening(text):
    """
    Replace repeated character sequences of length 3 or greater with sequences
    of length 3.
    """
    pattern = re.compile(r"(.)\1{2,}")
    return pattern.sub(r"\1\1\1", text)


######################################################################
# Tokenization Function
######################################################################

def incident_tokenize(text, preserve_case=True, reduce_len=False, strip_handles=False):
    """
    Convenience function for wrapping the tokenizer.
    """
    return IncidentTextTokenizer(preserve_case=preserve_case, strip_handles=True, reduce_len=True).tokenize(text)
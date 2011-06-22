##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Kirbi ISBN handling functions
"""

class InvalidISBN(ValueError):
    """This is not a valid ISBN-10 or ISBN-13"""

def filterDigits(input):
    """ Strip the input of all non-digits, but retain last X if present. """
    input = input.strip()
    digits = [c for c in input if c.isdigit()]
    # an X may appear as check digit in ISBN-10
    if len(input) and input[-1].upper() == 'X':
        digits.append('X')
    return ''.join(digits)

def checksumISBN10(digits):
    """ Return ISBN-10 check digit as a string of len 1 (may be 0-9 or X)
        References:
        http://www.isbn-international.org/en/userman/chapter4.html#usm4_4
        http://www.bisg.org/isbn-13/conversions.html
    """
    sum = 0
    for i, weight in enumerate(range(10,1,-1)):
        sum += int(digits[i]) * weight
    check = 11 - sum % 11
    if check == 10: return 'X'
    elif check == 11: return '0'
    return str(check)

def checksumEAN(digits):
    """ Return EAN check digit as a string (may be 0-9)
        Every ISBN-13 is a valid EAN
        Reference:
        http://www.bisg.org/isbn-13/conversions.html
    """
    sum = 0
    for i, d in enumerate(digits[:12]):
        weight = i%2*2+1
        sum += int(d) * weight
    check = 10 - sum % 10
    if check == 10: return '0'
    return str(check)

def validatedEAN(digits):
    if not digits:
        return None
    if len(digits) != 13:
        digits = filterDigits(digits)
        if len(digits) != 13:
            return None
    if digits[-1] == checksumEAN(digits):
        return digits

def validatedISBN10(digits):
    if not digits:
        return None
    if len(digits) != 10:
        digits = filterDigits(digits)
        if len(digits) != 10:
            return None
    if digits[-1] == checksumISBN10(digits):
        return digits

def validatedISBN13(digits):
    if not digits:
        return None
    if digits.strip()[:3] not in ['978','979']:
        return None
    return validatedEAN(digits)

def isValidISBN10(digits):
    return validatedISBN10(digits) is not None

def isValidISBN13(digits):
    return validatedISBN13(digits) is not None

def isValidEAN(digits):
    return validatedEAN(digits) is not None

def isValidISBN(digits):
    return isValidISBN10(digits) or isValidISBN13(digits)

def convertISBN10toISBN13(digits):
    if len(digits) > 10:
        digits = filterDigits(digits)
    if len(digits) != 10:
        raise InvalidISBN, '%s is not a valid ISBN-10' % digits
    else:
        digits = '978' + digits[:-1]
        return digits + checksumEAN(digits)

def convertISBN13toISBN10(digits):
    if len(digits) > 13:
        digits = filterDigits(digits)
    if len(digits) != 13:
        raise InvalidISBN, '%s is not a valid ISBN-13'
    if digits.startswith('978'):
        digits = digits[3:-1]
        return digits + checksumISBN10(digits)
    elif digits.startswith('979'):
        raise InvalidISBN, '%s is a valid ISBN-13 but has no ISBN-10 equivalent'
    else:
        raise InvalidISBN, '%s is not a valid ISBN-13 (wrong prefix)'

def toISBN13(digits):
    digits = filterDigits(digits)
    if isValidISBN13(digits): return digits
    else:
        return convertISBN10toISBN13(digits)

# Note: ISBN group identifiers related to languages
# http://www.isbn-international.org/en/identifiers/allidentifiers.html
# http://www.loc.gov/standards/iso639-2/php/code_list.php
lang_groups = {
    'en':(0,1),'fr':(2,),'de':(3,),'jp':(4,), 'ru':(5,),
    'es':(84,           # Spain
          950, 987,     # Argentina
          956,          # Chile
          958,          # Colombia
          959,          # Cuba
          968, 970,     # Mexico
          980,          # Venezuela
          9942, 9978,   # Ecuador
          9945, 99934,  # Dominican Republic
          9962,         # Panama
          9968,         # Costa Rica (and 9977)
          9972,         # Peru
          9974,         # Uruguay
          99922, 99939, # Guatemala
          99923,        # El Salvador
          99924,        # Nicaragua
          99925, 99953, # Paraguay
          99926,        # Honduras
         ),
    'pt':(85,           # Brazil
          972, 989,     # Portugal
         ),
    }

group_lang = {}

for lang, groups in lang_groups.iteritems():
    for group in groups:
        group_lang[str(group)] = lang

def convertISBN13toLang(isbn13):
    assert len(isbn13)==13
    registration_group_field = isbn13[3:8]
    for i in range(1,6):
        possible_group = registration_group_field[:i]
        if possible_group in group_lang:
            return group_lang[possible_group]
    return None

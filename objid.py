#
# Convert ASN1 Object ID's value between various representations.
#
# Written by Ilya Etingof <ilya@glas.net>, 2000
#

# import system modules
import string

# implement various convertions of ASN1 Object ID's value
class objid:
    # convert string type Object ID into a list of numeric sub ID's
    def str2nums (self, str=None):
        """convert string type Object ID into a list of numeric sub ID's"""
        # check the argument
        if not str:
            raise bad_argument

        # convert string into a list
        objid_s = string.split(str, '.')

        # filter out empty members (leading dot causes this)
        objid_s = filter(lambda x: len(x), objid_s)

        # convert a list of symbols into a list of numbers
        objid_n = map(lambda x: string.atol(x), objid_s)

        # make sure the convertion succeeded
        if not len(objid_n):
            raise illegal_argument, str

        # return the list of numerics
        return objid_n

    # convert a list of numeric sub ID's into string
    def nums2str (self, objid_n=None):
        """convert a list of numeric sub ID's into string"""
        # check the argument
        if objid_n == None:
            raise bad_argument

        # convert a list of number into a list of symbols
        objid_s = map(lambda x: '.%lu' % x, objid_n)
 
        # merge all the list members into a string
        str = reduce(lambda x, y: x+y, objid_s)

        # make sure the convertion succeeded
        if not len(str):
            raise illegal_argument

        # return the string
        return str


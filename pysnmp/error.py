"""
   Root exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002. Suggested by
   Case Van Horsen <case@ironwater.com>.
"""   
import exceptions

class PySnmpError(exceptions.Exception):
    """Base class for PySNMP error handlers
    """
    def __init__(self, err_msg=None):
        """
        """
        exceptions.Exception.__init__(self)

        if err_msg is not None:
            self.err_msg = str(err_msg)
        else:
            self.err_msg = ''

    def __str__(self):
        """
        """
        return self.err_msg

    def __repr__(self):
        """
        """
        return self.__class__.__name__ + '(' + self.err_msg + ')'

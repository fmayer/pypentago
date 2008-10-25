# pyPentago - a board game
# Copyright (C) 2008 Florian Mayer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import logging

from wx import PyValidator
from pypentago import EMAIL_REGEX


class Validator(PyValidator):
    """ Baseclass for all validators. Everything passed to its __init__ will be 
    passed to the subclass in the Clone method. This means you have to pass 
    everything the __init__ of your validator takes to this. 
    
    Also implements dummy TransferToWindow and TransferFromWindow to prevent wx 
    from complaining
    """
    def __init__(self, *args, **kwargs):
        PyValidator.__init__(self)
        self.args = args
        self.kwargs = kwargs
        
    def Clone(self):
        return self.__class__(*self.args, **self.kwargs)

    def TransferToWindow(self):
        return True # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True # Prevent wxDialog from complaining.


class ValidateName(Validator):
    def __init__(self, parent):
        Validator.__init__(self, parent)
        self.parent = parent

    def Validate(self, win):
        return self.parent.available


class ValidateEmail(Validator):
    def __init__(self):
        Validator.__init__(self)
        self.email = re.compile(EMAIL_REGEX, re.IGNORECASE)
        self.log = logging.getLogger("pypentago.validator")

    def Validate(self, win):
        self.log.debug("In ValidateEmail.Validate")
        tc = self.GetWindow()
        val = tc.GetValue()
        return self.email.match(val)

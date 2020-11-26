"""
UBXMultiMessage class.

Reads and parses multiple UBX messages

Returns the parsed data (as a UBXMessage object).

If the 'validate' parameter is set to 'True', the reader will raise a UBXMultiMessageError if
it encounters any non-UBX data. Otherwise, it will ignore the non-UBX data and attempt
to carry on.

Created on 26 Nov 2020

@author: guillemfrancisco
"""

from pyubx2.ubxmessage import UBXMessage
from pyubx2.exceptions import UBXMessageError
import pyubx2.ubxtypes_core as ubt


class UBXMultiMessage:
    """
    UBXMultiMessage class.
    """

    def __init__(self, ubxs, validate=False):
        """Constructor.

        :params ubxs: ubxs
        :params validate: bool

        """

        self._ubxs = ubxs
        self._validate = validate

    def read(self) -> [UBXMessage]:
        """Read the multiple UBX messages

        :return [UBXMessage]:

        """

        stm = self._ubxs
        lenm = len(stm)
        i = 0
        ubxs_parsed = []

        while i < lenm:
            byte1 = stm[i:i+2] # HEADER
            if len(byte1) < 2:  # EOF
                break
            if byte1 == ubt.UBX_HDR:  # it's a UBX message
                byten = stm[i+2:i+6]
                if len(byten) < 4:  # EOF
                    break
                clsid = byten[0:1]
                msgid = byten[1:2]
                lenb = byten[2:4]
                leni = int.from_bytes(lenb, "little", signed=False)
                byten = stm[i+6:i+(6 + leni + 2)]
                if len(byten) < leni + 2:  # EOF
                    break
                plb = byten[0:leni]
                cksum = byten[leni:(leni + 2)]
                raw_data = ubt.UBX_HDR + clsid + msgid + lenb + plb + cksum
                parsed_data = UBXMessage.parse(raw_data)
                ubxs_parsed.append(parsed_data)
                i = i + 6 + leni + 2
            else:  # it's not a UBX message
                if self._validate:  # raise error and quit
                    raise UBXMessageError(f"Unknown data header {byte1}")
                i = i+2  # read next 2 bytes and carry on

        return ubxs_parsed

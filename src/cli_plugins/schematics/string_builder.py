"""
Implementation of a string builder to help with efficient string creation.
"""
import io


class StringBuilder:
    """
    Implementation of a string builder to help with efficient string creation.
    """

    def __init__(self):
        self._stringio = io.StringIO()

    def __str__(self):
        return self._stringio.getvalue()

    def append(self, *objects, sep=" ", end=""):
        """
        Appends the provided string to the existing string.  Does not include new line.

        sep provides seperators between provided strings.
        end what is appended to the end of the line.
        """
        print(*objects, sep=sep, end=end, file=self._stringio)

    def append_line(self, *objects, sep=" "):
        """
        Appends the provided string to the existing string.  Includes a new line.

        sep provides seperators between provided strings.
        """
        self.append(*objects, sep=sep, end="\n")

import io


class StringBuilder(object):
    def __init__(self):
        self._stringio = io.StringIO()

    def __str__(self):
        return self._stringio.getvalue()

    def append(self, *objects, sep=" ", end=""):
        print(*objects, sep=sep, end=end, file=self._stringio)

    def append_line(self, *objects, sep=" "):
        self.append(*objects, sep=sep, end="\n")

import numpy as np
import pathlib as pl


class RDF(object):
    _MAX_VALUE = 0x3fff
    _MIN_VALUE = 0x0
    DATA_LENGTH = 4096

    def __init__(self, sequence):
        self.check_sequence(sequence)
        self.sequence = self._to_rdf(sequence)

    def check_sequence(self, sequence):
        assert len(sequence) == self.DATA_LENGTH, \
            f"Sequence has to be of length {self.DATA_LENGTH}, but is of length {len(sequence)}"

    def _to_rdf(self, sequence):
        sequence = np.array(sequence)
        sequence = ((sequence / max(sequence)) * self._MAX_VALUE).round().astype(np.int16)
        return sequence

    def save(self, path: pl.Path):
        self.sequence.tofile(path)

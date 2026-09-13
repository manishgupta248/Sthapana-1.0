class SthapanaError(Exception):
    """
    Base class for all custom, project-specific errors.
    Catching this (instead of a bare 'Exception') lets us handle
    'things we expected might go wrong' distinctly from genuine bugs.
    """
    pass


class RecordLockedError(SthapanaError):
    """
    Example of a specific error a later phase might raise -
    e.g. trying to edit an office record that's locked for review.
    Not used yet in Phase 0; included as the pattern to follow later.
    """
    pass
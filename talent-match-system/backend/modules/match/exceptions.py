class MatchException(Exception):
    pass


class ResumeNotFoundException(MatchException):
    pass


class JobNotFoundException(MatchException):
    pass


class MatchNotFoundException(MatchException):
    pass
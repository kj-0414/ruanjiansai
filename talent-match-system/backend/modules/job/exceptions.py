class JobException(Exception):
    pass


class JobNotFoundException(JobException):
    pass


class AccessDeniedException(JobException):
    pass
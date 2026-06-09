class ResumeException(Exception):
    pass


class InvalidFileTypeException(ResumeException):
    pass


class FileSizeExceededException(ResumeException):
    pass


class ResumeNotFoundException(ResumeException):
    pass


class AccessDeniedException(ResumeException):
    pass
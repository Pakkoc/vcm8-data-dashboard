"""
Custom exceptions for data upload operations
"""


class InvalidFileFormatError(Exception):
    """파일 형식이 올바르지 않을 때 발생"""

    pass


class FileParsingError(Exception):
    """파일 파싱 중 오류 발생 시"""

    pass


class DataValidationError(Exception):
    """데이터 검증 실패 시 발생"""

    def __init__(self, errors):
        self.errors = errors if isinstance(errors, list) else [errors]
        super().__init__(str(self.errors))

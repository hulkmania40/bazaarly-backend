class BazaarlyError(Exception):
    code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str = "An unexpected error occurred", code: str | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        if code:
            self.code = code


class NotFoundError(BazaarlyError):
    code = "NOT_FOUND"


class ForbiddenError(BazaarlyError):
    code = "FORBIDDEN_ROLE"


class ConflictError(BazaarlyError):
    code = "CONFLICT"


class ValidationError(BazaarlyError):
    code = "VALIDATION_ERROR"

from fastapi import status


class MissingPermissionKeyword(Exception):
    def __init__(self, keyword):
        self.keyword = keyword
        self.message = "missing keyword for permission: {}".format(keyword)
        self.http_error_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(self.message)


class NoPermissionDefinitionForRoute(Exception):
    def __init__(self, message="The permission definition for this route does not exist."):
        self.message = message
        self.http_error_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(self.message)


class PermissionDenied(Exception):
    def __init__(self, message="You do not have permission to access this resource"):
        self.message = message
        self.http_error_status = status.HTTP_401_UNAUTHORIZED
        super().__init__(self.message)


class PermissionExpressionMalformed(Exception):
    def __init__(self, expression):
        self.expression = expression
        self.message = "Permission expression for this route is malformed: {}".format(expression)
        self.http_error_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(self.message)

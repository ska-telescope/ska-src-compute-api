import requests
import traceback
from functools import wraps

from fastapi import HTTPException, status


def handle_client_exceptions(func):
    """ Decorator to handle client exceptions. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            detail = f"HTTP error occurred: {e}, response: {e.response.text}"
            raise HTTPException(status_code=status_code, detail=detail)
        except HTTPException as e:
            raise e
        except CustomException as e:
            raise Exception(message=e.message)
        except CustomHTTPException as e:
            raise HTTPException(status_code=e.http_error_status, detail=e.message)
        except Exception as e:
            detail = "General error occurred: {}, traceback: {}".format(
                repr(e), ''.join(traceback.format_tb(e.__traceback__)))
            raise HTTPException(status_code=500, detail=detail)
    return wrapper


def handle_exceptions(func):
    """ Decorator to handle server exceptions. """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            detail = f"HTTP error occurred: {e}, response: {e.response.text}"
            raise HTTPException(status_code=status_code, detail=detail)
        except HTTPException as e:
            raise e
        except CustomException as e:
            raise Exception(message=e.message)
        except CustomHTTPException as e:
            raise HTTPException(status_code=e.http_error_status, detail=e.message)
        except Exception as e:
            detail = "General error occurred: {}, traceback: {}".format(
                repr(e), ''.join(traceback.format_tb(e.__traceback__)))
            raise HTTPException(status_code=500, detail=detail)
    return wrapper


class CustomException(Exception):
    """ Class that all custom exceptions must inherit in order for exception to be caught by the
    handle_exceptions decorator.
    """
    pass


class CustomHTTPException(Exception):
    """ Class that all custom HTTP exceptions must inherit in order for exception to be caught by
    the handle_exceptions decorator.
    """
    pass


class PermissionDenied(CustomHTTPException):
    def __init__(self):
        self.message = "You do not have permission to access this resource."
        self.http_error_status = status.HTTP_403_FORBIDDEN
        super().__init__(self.message)

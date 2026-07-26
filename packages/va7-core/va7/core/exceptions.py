import logging

from rest_framework.views import exception_handler

logger = logging.getLogger("va7.core")


def custom_exception_handler(exc, context):
    """
    DRF exception handler with standardized error format.

    Response format:
        {
            "success": false,
            "message": "An error occurred.",
            "errors": {"field": ["error messages"]}
        }

    Combines:
    - Standardized response format (Triscaleon pattern)
    - Exception logging (PGPulse pattern)
    - Critical logging for 500-level errors
    """
    view_name = getattr(context.get("view"), "__class__", type(None)).__name__
    logger.error("API Exception in %s: %s", view_name, exc, exc_info=True)

    response = exception_handler(exc, context)

    if response is None:
        logger.critical("Unhandled exception in %s: %s", view_name, exc, exc_info=True)
        return None

    errors = response.data

    # Normalize error format
    if isinstance(errors, list):
        errors = {"non_field_errors": errors}
    elif isinstance(errors, dict) and "detail" in errors:
        errors = {"non_field_errors": [errors["detail"]]}

    response.data = {
        "success": False,
        "message": "An error occurred.",
        "errors": errors,
    }

    if response.status_code >= 500:
        logger.critical("Server error in %s: %s", view_name, exc, exc_info=True)

    return response

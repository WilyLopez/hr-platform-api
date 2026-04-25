from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from shared.domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    EntityAlreadyExistsException,
    InvalidValueException,
    BusinessRuleViolationException,
    UnauthorizedOperationException,
    InactiveEntityException,
    TenantIsolationException,
    ExternalServiceException,
)


DOMAIN_EXCEPTION_STATUS_MAP = {
    EntityNotFoundException: status.HTTP_404_NOT_FOUND,
    EntityAlreadyExistsException: status.HTTP_409_CONFLICT,
    InvalidValueException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    BusinessRuleViolationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    UnauthorizedOperationException: status.HTTP_403_FORBIDDEN,
    InactiveEntityException: status.HTTP_403_FORBIDDEN,
    TenantIsolationException: status.HTTP_403_FORBIDDEN,
    ExternalServiceException: status.HTTP_502_BAD_GATEWAY,
}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, DomainException):
        http_status = DOMAIN_EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "status": "error",
                "code": exc.code,
                "message": exc.message,
            },
            status=http_status,
        )

    if response is not None:
        return Response(
            {
                "status": "error",
                "code": _resolve_drf_code(response.status_code),
                "message": _extract_drf_message(response.data),
                "detail": response.data,
            },
            status=response.status_code,
        )

    return Response(
        {
            "status": "error",
            "code": "internal_server_error",
            "message": "Ha ocurrido un error interno en el servidor.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _resolve_drf_code(status_code: int) -> str:
    codes = {
        400: "bad_request",
        401: "authentication_failed",
        403: "permission_denied",
        404: "not_found",
        405: "method_not_allowed",
        429: "throttled",
    }
    return codes.get(status_code, "error")


def _extract_drf_message(data) -> str:
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        first_key = next(iter(data), None)
        if first_key:
            first_value = data[first_key]
            if isinstance(first_value, list) and first_value:
                return f"{first_key}: {first_value[0]}"
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)
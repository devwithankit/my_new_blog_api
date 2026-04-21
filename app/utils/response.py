def SuccessResponse(message: str, status_code: int = 200, data=None):
    return {
        "status_code": status_code,
        "message": message,
        "data": data or {}  
    }

def ErrorResponse(message: str, status_code: int = 400):
    return {
        "status_code": status_code,
        "message": message,
        "data": {}
    }
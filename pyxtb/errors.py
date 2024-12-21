from ._types import ERROR_RESPONSE

CODES = {
    "BE001": "Invalid price",
    "BE002": "Invalid StopLoss or TakeProfit",
    "BE003": "Invalid volume",
    "BE004": "Login disabled",
    "BE005": "userPasswordCheck: Invalid login or password.",
    "BE006": "Market for instrument is closed",
    "BE007": "Mismatched parameters",
    "BE008": "Modification is denied",
    "BE009": "Not enough money on account to perform trade",
    "BE010": "Off quotes",
    "BE011": "Opposite positions prohibited",
    "BE012": "Short positions prohibited",
    "BE013": "Price has changed",
    "BE014": "Request too frequent",
    "BE016": "Too many trade requests",
    "BE017": "Too many trade requests",
    "BE018": "Trading on instrument disabled",
    "BE019": "Trading timeout",
    "BE020": "Other error",
    "BE021": "Other error",
    "BE022": "Other error",
    "BE023": "Other error",
    "BE024": "Other error",
    "BE025": "Other error",
    "BE026": "Other error",
    "BE027": "Other error",
    "BE028": "Other error",
    "BE029": "Other error",
    "BE030": "Other error",
    "BE031": "Other error",
    "BE032": "Other error",
    "BE033": "Other error",
    "BE034": "Other error",
    "BE035": "Other error",
    "BE036": "Other error",
    "BE037": "Other error",
    "BE099": "Other error",
    "BE094": "Symbol does not exist for given account",
    "BE095": "Account cannot trade on given symbol",
    "BE096": "Pending order cannot be closed. Pending order must be deleted",
    "BE097": "Cannot close already closed order",
    "BE098": "No such transaction",
    "BE101": "Unknown instrument symbol",
    "BE102": "Unknown transaction type",
    "BE103": "User is not logged",
    "BE104": "Method does not exist",
    "BE105": "Incorrect period given",
    "BE106": "Missing data",
    "BE110": "Incorrect command format",
    "BE115": "Symbol does not exist",
    "BE116": "Symbol does not exist",
    "BE117": "Invalid token",
    "BE118": "User already logged",
    "BE200": "Session timed out.",
    "EX000": "Invalid parameters",
    "EX001": "Internal error, in case of such error, please contact support",
    "EX002": "Internal error, in case of such error, please contact support",
    "SExxx": "Internal error, in case of such error, please contact support",
    "BE000": "Internal error, in case of such error, please contact support",
    "EX003": "Internal error, request timed out",
    "EX004": "Login credentials are incorrect or this login is not allowed to use an application with this appId",
    "EX005": "Internal error, system overloaded",
    "EX006": "No access",
    "EX007": "userPasswordCheck: Invalid login or password. This login/password is disabled for 10 minutes (the specific login and password pair is blocked after an unsuccessful login attempt).",
    "EX008": "You have reached the connection limit. For details see the Connection validation section.",
    "EX009": "Data limit potentially exceeded. Please narrow your request range. The potential data size is calculated by: (end_time - start_time) / interval. The limit is 50 000 candles",
    "EX010": "Your login is on the black list, perhaps due to previous misuse. For details please contact support.",
    "EX011": "You are not allowed to execute this command. For details please contact support.",
}


def handle_error(response: ERROR_RESPONSE):
    """
    Handles an error response from the API.

    Args:
        response (ERROR_RESPONSE): The error response containing error code and description.

    Raises:
        Exception: Raises an exception with the error description.
    """
    code = response["errorCode"]
    if code.startswith("SE"):
        raise Exception("Internal error, in case of such error, please contact support")
    if code in CODES:
        raise Exception(CODES[code])
    raise Exception(response["errorDescr"])

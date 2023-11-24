from uuid import UUID
import datetime
import decimal


def normalised_response(result_object):
    """
    :param result_object:
    :return:
    """
    decoded_response = []
    for rowproxy in result_object:
        new_row = {}
        rowproxy.item()
        for column, value in rowproxy.items():
            new_value = value
            if isinstance(value, UUID):
                new_value = str(value)
            if isinstance(value, (datetime.date, datetime.datetime)):
                new_value = value.isoformat()
            new_row[column] = new_value
        decoded_response.append(new_row)
    return decoded_response


def format_text(text):
    return text.replace("'", "''").replace("%", "%%")


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj

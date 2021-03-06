
import logging
from typing import Optional, Mapping

log = logging.getLogger(__name__)

# Number of digits after the decimal point for temperatures being sent
# to/from Temp-Deck
GCODE_ROUNDING_PRECISION = 0


class ParseError(Exception):
    pass


def parse_string_value_from_substring(substring) -> str:
    '''
    Returns the ascii value in the expected string "N:aa11bb22", where "N" is
    the key, and "aa11bb22" is string value to be returned
    '''
    try:
        value = substring.split(':')[1]
        return str(value)
    except (ValueError, IndexError, TypeError, AttributeError):
        log.exception('Unexpected arg to parse_string_value_from_substring:')
        raise ParseError(
            'Unexpected arg to parse_string_value_from_substring: {}'.format(
                substring))


def parse_number_from_substring(substring) -> Optional[float]:
    '''
    Returns the number in the expected string "N:12.3", where "N" is the
    key, and "12.3" is a floating point value

    For the temp-deck or thermocycler's temperature response, one expected
    input is something like "T:none", where "none" should return a None value
    '''
    try:
        value = substring.split(':')[1]
        if value.strip().lower() == 'none':
            return None
        return round(float(value), GCODE_ROUNDING_PRECISION)
    except (ValueError, IndexError, TypeError, AttributeError):
        log.exception('Unexpected argument to parse_number_from_substring:')
        raise ParseError(
            'Unexpected argument to parse_number_from_substring: {}'.format(
                substring))


def parse_key_from_substring(substring) -> str:
    '''
    Returns the axis in the expected string "N:12.3", where "N" is the
    key, and "12.3" is a floating point value
    '''
    try:
        return substring.split(':')[0]
    except (ValueError, IndexError, TypeError, AttributeError):
        log.exception('Unexpected argument to parse_key_from_substring:')
        raise ParseError(
            'Unexpected argument to parse_key_from_substring: {}'.format(
                substring))


def parse_temperature_response(
        temperature_string: str) -> Mapping[str, Optional[float]]:
    '''
    Example input: "T:none C:25"
    '''
    err_msg = 'Unexpected argument to parse_temperature_response: {}'.format(
        temperature_string)
    if not temperature_string or \
            not isinstance(temperature_string, str):
        raise ParseError(err_msg)
    parsed_values = temperature_string.strip().split(' ')
    if len(parsed_values) < 2:
        log.error(err_msg)
        raise ParseError(err_msg)

    data = {
        parse_key_from_substring(s): parse_number_from_substring(s)
        for s in parsed_values[:2]
    }
    if 'C' not in data or 'T' not in data:
        raise ParseError(err_msg)
    data = {
        'current': data['C'],
        'target': data['T']
    }
    return data


def parse_device_information(
        device_info_string: str) -> Mapping[str, str]:
    '''
        Parse the modules's device information response.

        Example response from temp-deck: "serial:aa11 model:bb22 version:cc33"
    '''
    error_msg = 'Unexpected argument to parse_device_information: {}'.format(
        device_info_string)
    if not device_info_string or \
            not isinstance(device_info_string, str):
        raise ParseError(error_msg)
    parsed_values = device_info_string.strip().split(' ')
    if len(parsed_values) < 3:
        log.error(error_msg)
        raise ParseError(error_msg)
    res = {
        parse_key_from_substring(s): parse_string_value_from_substring(s)
        for s in parsed_values[:3]
    }
    for key in ['model', 'version', 'serial']:
        if key not in res:
            raise ParseError(error_msg)
    return res

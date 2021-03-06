import sys
import traceback
import re
from itertools import islice
from datetime import datetime
from tilequeue.tile import coord_marshall_int
from tilequeue.tile import create_coord


def format_stacktrace_one_line(exc_info=None):
    # exc_info is expected to be an exception tuple from sys.exc_info()
    if exc_info is None:
        exc_info = sys.exc_info()
    exc_type, exc_value, exc_traceback = exc_info
    exception_lines = traceback.format_exception(exc_type, exc_value,
                                                 exc_traceback)
    stacktrace = ' | '.join([x.replace('\n', '')
                             for x in exception_lines])
    return stacktrace


def grouper(iterable, n):
    """Yield n-length chunks of the iterable"""
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        yield chunk


def parse_log_file(log_file):
    ip_pattern = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    # didn't match againts explicit date pattern, in case it changes
    date_pattern = '\[([\d\w\s\/:]+)\]'
    tile_id_pattern = '\/([\w]+)\/([\d]+)\/([\d]+)\/([\d]+)\.([\d\w]*)'

    log_pattern = '%s - - %s "([\w]+) %s.*' % (
        ip_pattern, date_pattern, tile_id_pattern)

    tile_log_records = []
    for log_string in log_file:
        match = re.search(log_pattern, log_string)
        if match and len(match.groups()) == 8:
            tile_log_records.append(
                (match.group(1),
                 datetime.strptime(match.group(2), '%d/%B/%Y %H:%M:%S'),
                 coord_marshall_int(
                     create_coord(
                         match.group(6), match.group(7), match.group(5)))))

    return tile_log_records


def encode_utf8(x):
    if x is None:
        return None
    elif isinstance(x, unicode):
        return x.encode('utf-8')
    elif isinstance(x, dict):
        result = {}
        for k, v in x.items():
            if isinstance(k, unicode):
                k = k.encode('utf-8')
            result[k] = encode_utf8(v)
        return result
    elif isinstance(x, list):
        return map(encode_utf8, x)
    elif isinstance(x, tuple):
        return tuple(encode_utf8(list(x)))
    else:
        return x

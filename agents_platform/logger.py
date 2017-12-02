# please, pay attention to 'current_level'
# messages with level that is lower than 'current_level' will not be logged
# messages with level that is lower that 'console_level' will not be written to console
# usage:
#
# import logger
#
#
# logger.debug('current_module_name', 'debug')
# logger.info('current_module_name', 'information')
# logger.warning('current_module_name', 'warning')
# logger.error('current_module_name', 'error')
# logger.exception('current_module_name', 'exception')

import datetime
import os

LOGS_DIRECTORY_PATH = ''

known_loggers = ['own_adapter', 'helloworld']
levels = {'Debug': 0, 'Info': 1, 'Warning': 2, 'Error': 3, 'Exception': 4}

# we can get the level from config, or change it while debugging
current_level = 'Debug'
console_level = 'Debug'


# returns True if writing to a file was successful, and False - in other cases
def __log_message(logger_name, message, level):
    result = False

    if logger_name not in known_loggers:
        return result

    if levels[level] >= levels[current_level]:
        now = datetime.datetime.utcnow()
        formatted_time = now.strftime('%Y.%m.%d %H:%M:%S')
        formatted_day = now.strftime('%Y.%m.%d')
        log_message = '{0} [{1}] {2}'.format(formatted_time, level, message)

        # write to a file
        try:
            logs_directory = '{0}/{1}'.format(LOGS_DIRECTORY_PATH, logger_name)

            if not os.path.exists(logs_directory):
                os.makedirs(logs_directory)

            log_file_name = '{}/{}.log'.format(logs_directory, formatted_day)
            with open(log_file_name, 'a', encoding='utf-8') as log_file:
                print(log_message, file=log_file)
            result = True
        except OSError as e:
            try_print_to_console('Directory for logs was not created. Error message: {}'.format(str(e)))
        except KeyError as e:
            try_print_to_console(
                'The OWN_AGENTS_PATH environment variable is not defined. Error message: {}'.format(str(e)))
        except Exception as e:
            try_print_to_console('File handler for logs was not created. Exception message: {}'.format(str(e)))

        # write to console
        try:
            if levels[level] >= levels[console_level]:
                print(log_message)
        except Exception as e:
            try_print_to_console('Console handler for logs was not created. Error message: {}'.format(str(e)))

    return result


# wrappers for different levels
def debug(logger_name, message):
    return __log_message(logger_name, message, 'Debug')


def info(logger_name, message):
    return __log_message(logger_name, message, 'Info')


def warning(logger_name, message):
    return __log_message(logger_name, message, 'Warning')


def error(logger_name, message):
    return __log_message(logger_name, message, 'Error')


def exception(logger_name, message):
    return __log_message(logger_name, message, 'Exception')


def try_print_to_console(message):
    try:
        print(message)
    except:
        pass

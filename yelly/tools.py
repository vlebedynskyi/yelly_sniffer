import logging
import os
import errno

logger = logging.getLogger(__name__)


def dump_to_file(file_path, content):
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(file_path, 'w') as outfile:
        outfile.writelines(content)

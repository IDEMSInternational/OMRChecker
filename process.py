"""

 OMRChecker

 Author: Udayraj Deshmukh
 Github: https://github.com/Udayraj123

"""

import argparse
from pathlib import Path

from src.entry import entry_point, process_single_file
from src.logger import logger


def parse_args():
    # construct the argument parse and parse the arguments
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        type=str,
        dest="input_path",
        help="Specify an input image.",
    )

    argparser.add_argument(
        dest="template_path",
        help="Specify an output directory.",
    )

    args, unknown, = argparser.parse_known_args()

    if len(unknown) > 0:
        logger.warning(f"\nError: Unknown arguments: {unknown}", unknown)
        argparser.print_help()
        exit(11)

    return args


if __name__ == "__main__":
    args = parse_args()
    process_single_file(args.input_path, Path(args.template_path))

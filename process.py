"""

 OMRChecker

 Author: Udayraj Deshmukh
 Github: https://github.com/Udayraj123

"""

import argparse
from pathlib import Path
import uuid
import json

from src.entry import entry_point, process_single_file, process_from_url


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
    # out = process_from_url(args.input_path, Path(args.template_path))
    out = process_single_file(args.input_path, Path(args.template_path))
    # out['uuid'] = str(uuid.uuid4())
    print(json.dumps(out))

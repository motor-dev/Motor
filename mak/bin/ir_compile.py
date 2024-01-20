if __name__ == '__main__':
    import argparse
    import sys

    argument_context = argparse.ArgumentParser()
    argument_context.add_argument(
        "-t",
        "--tmp",
        dest="tmp_dir",
        help="Directory to store temporary/cached files",
        default=".",
    )
    argument_context.add_argument(
        "input",
        help="Input LLVM source file",
        metavar="IN",
    )
    argument_context.add_argument(
        "output",
        help="Output translated file",
        metavar="OUT",
    )
    argument_context.add_argument(
        "processor",
        help="Processor module",
        metavar="PROCESSOR",
    )
    arguments = argument_context.parse_args()
    with open(arguments.output, 'w') as output_file:
        pass

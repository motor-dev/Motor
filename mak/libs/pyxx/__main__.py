from . import init_arguments, run

if __name__ == '__main__':
    arguments = init_arguments()
    run(arguments.parse_args())
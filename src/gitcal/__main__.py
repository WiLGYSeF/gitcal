import sys

from . import __version__, args, gitcal

def main():
    print(draw_tables_from_args(sys.argv[1:]))

def draw_tables_from_args(argv):
    argspace, table_configs = args.parse_args(argv)

    if argspace.version:
        print(__version__)
        sys.exit(0)

    args.append_table_config(argspace, table_configs)
    return gitcal.draw_tables(argspace, table_configs)

if __name__ == '__main__': #pragma: no cover
    main()

import sys

from gitcal import args
from gitcal import gitcal

def main():
    print(draw_tables_from_args(sys.argv[1:]))

def draw_tables_from_args(argv):
    argspace, table_configs = args.parse_args(argv)
    args.append_table_config(argspace, table_configs)
    return gitcal.draw_tables(argspace, table_configs)

if __name__ == '__main__': #pragma: no cover
    main()

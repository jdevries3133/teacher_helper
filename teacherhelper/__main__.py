"""Teacher Heper CLI"""

import argparse
import code
import sys

from .sis import Sis


sis = Sis.read_cache() if Sis.cache_exists() else None

if sis is None:
    print('fatal: cache does not exist')
    sys.exit()


def find_student(name):
    print(sis.find_student(name, threshold=60))


def find_parent(name):
    print(sis.find_parent(name))


def shell():
    code.interact(
        local={
            "sis": sis,
        }
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--student", "-s", help="Lookup a student and print the result")
    parser.add_argument("--parent", "-p", help="Lookup a parent and print the result")
    parser.add_argument(
        "--new",
        action="store_const",
        const=True,
        help=(
            "Regenerate the database by parsing student.csv and parent.csv "
            "in the $HELPER_DATA directory."
        ),
    )

    args = parser.parse_args()

    if args.new:
        Sis.new_school_year().write_cache()
    elif args.student:
        find_student(args.student)
    elif args.parent:
        find_parent(args.parent)
    else:
        shell()


if __name__ == "__main__":
    main()

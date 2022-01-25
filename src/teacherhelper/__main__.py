"""Teacher Heper CLI"""

import code
import argparse

from .helper import Helper


helper = Helper.read_cache() if Helper.cache_exists() else None


def find_student(name):
    assert helper is not None
    print(helper.find_nearest_match(name, threshold=60))


def find_parent(name):
    assert helper is not None
    print(helper.find_parent(name))


def shell():
    code.interact(
        local={
            "helper": helper,
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
        Helper.new_school_year().write_cache()
    elif args.student:
        find_student(args.student)
    elif args.parent:
        find_parent(args.parent)
    else:
        shell()


if __name__ == "__main__":
    main()

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Callable

from commands import queries
from models import Store
from store import load_tasks, save_tasks


def parse_cli() -> tuple[Callable, dict, Path]:
    """
    Parse CLI arguments into the query function, its kwargs, and the store path.

    Builds subcommands from task_ops.queries, parses args with argparse, and
    returns (query, args, store_path) where:
      - query is the callable for the chosen command
      - args is a dict of parsed arguments (excluding command and store)
      - store_path is an absolute Path to the JSON store (must not be a directory)
    """
    parser: ArgumentParser = ArgumentParser(
        description="This is a CLI task manager made so you can track your everyday tasks."
    )
    parser.add_argument(
        "--store",
        help="Path to your task store (default: 'tasks.json')",
        default="tasks.json",
    )
    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)
    for name, props in queries.items():
        p = subparsers.add_parser(name, help=props["help"])
        for arg in props["args"]:
            name = arg.pop("name")
            p.add_argument(*name, **arg)
            arg["name"] = name

    args: dict = vars(parser.parse_args())
    query: Callable = queries[args.pop("command")]["command"]
    store_path: Path = Path(args.pop("store")).expanduser().resolve()
    if store_path.is_dir():
        parser.error(f"Task Store path '{store_path}' is a directory")

    return query, args, store_path


def main() -> None:
    query, args, store_path = parse_cli()
    store: Store = load_tasks(store_path)
    try:
        query(store, **args)
    except Exception as e:
        sys.exit(str(e))
    save_tasks(store, store_path)


if __name__ == "__main__":
    main()

import argparse


def main() -> None:
    """Prints a greeting."""
    parser = argparse.ArgumentParser(description="Print a friendly greeting")
    parser.add_argument(
        "--name",
        default="world",
        help="Name to greet",
    )
    args = parser.parse_args()
    print(f"Hello, {args.name}")


if __name__ == "__main__":
    main()

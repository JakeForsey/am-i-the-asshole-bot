import argparse


def main():
    """
    Runs the bot.
    :return: None
    """

    # TODO (Sam) Write a loop that checks for posts then comments on them (comment can be nonsense for now)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--example_arg")

    args = argument_parser.parse_args()

    main()

import sys
import unittest
import argparse

def hierarcal_cli() :
    # Create the top-level parser
    parser = argparse.ArgumentParser(description = 'My CLI tool')
    subparsers = parser.add_subparsers(title = 'Commands', dest = 'command')

    # Create a subparser for the "foo" command
    foo_parser = subparsers.add_parser('foo', help = 'Do foo things')
    foo_parser.add_argument('foo_arg', help = 'A required argument for the "foo" command')

    # Create a subparser for the "bar" command
    bar_parser = subparsers.add_parser('bar', help = 'Do bar things')
    subsubparsers = bar_parser.add_subparsers(title = 'Bar commands', dest = 'bar_command')

    # Create a subparser for the "bar baz" subcommand
    baz_parser = subsubparsers.add_parser('baz', help = 'Do baz things')
    baz_parser.add_argument('baz_arg', help = 'A required argument for the "bar baz" command')

    # Create a subparser for the "bar qux" subcommand
    qux_parser = subsubparsers.add_parser('qux', help = 'Do qux things')
    qux_parser.add_argument('--qux-arg', help = 'An optional argument for the "bar qux" command')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Handle the parsed arguments based on the command and subcommand
    if args.command == 'foo' :
        print(f'Doing foo things with foo_arg={args.foo_arg}')
    elif args.command == 'bar' :
        if args.bar_command == 'baz' :
            print(f'Doing baz things with baz_arg={args.baz_arg}')
        elif args.bar_command == 'qux' :
            print(f'Doing qux things with qux_arg={args.qux_arg}')

if __name__ == '__main__':
    # sys.argv = ['_18_Argparse2', 'foo', 'some_arg']
    # sys.argv = ['_18_Argparse2', 'bar',  'baz',  'some_other_arg']
    sys.argv = ['_18_Argparse2', 'bar', 'qux', '--qux-arg', 'some_optional_arg']
    hierarcal_cli()

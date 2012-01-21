"""Entry point for Volt
"""

import argparse
import os
import sys

from volt import server


def build_parsers():
    """Build parser for arguments.
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands',
                                       help='Valid commands',
                                      )
    # parser for serve
    server_parser = subparsers.add_parser('serve', 
                                          help="Serves 'site' directory if \
                                                  present, otherwise serves \
                                                  current directory",
                                         )
    server_parser.add_argument('-d', '--dir', dest='server_dir',
                               metavar='DIR',
                               help='directory to serve',
                              )
    server_parser.add_argument('-p', '--port', dest='server_port',
                               default='8000', type=int,
                               metavar='PORT',
                               help='server port',
                              )
    server_parser.set_defaults(func=run_server)

    return parser

def run_server(options):
    """Runs the volt server.
    """
    server.run(options)

def main():
    """Main execution routine.
    """
    parser = build_parsers()
    options = parser.parse_args()
    options.func(options)

#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='commands')

# check command

checkParser = subparsers.add_parser("check", help='Check last entry')
checkParser.add_argument("presence", "serverstate", action = "store", help = "DB table to check")

insertParser = subparsers.add_parser("insert", help = "insert value into table")
insertParser.add_argument("presence", "serverstate", action = "store", help = "DB table to insert")
insertParser.add_argument("true", "false", action = "store", help = "value to insert")

print(parser.parse_args())
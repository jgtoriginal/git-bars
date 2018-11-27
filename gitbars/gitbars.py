#!/usr/bin/python

"""
git-bars produces a simple commit visualisation for a git repository.

git-bars is a Python utility that uses 'git log'
to produce a simple bar graph visualisation for
commit activity in a git repository.

Kailash Nadh, https://nadh.in

Licensed under the MIT License.
"""

import sys
from subprocess import check_output
import argparse
from collections import OrderedDict


def print_bars(items, block=u"\u2580", width=50):
    """Print unicode bar representations of dates and scores."""
    for i in items:
        num = str(items[i][0])

        sys.stdout.write(i)
        sys.stdout.write("  ")
        sys.stdout.write(num)
        sys.stdout.write((5 - len(num)) * " ")
        sys.stdout.write(block * int(items[i][1] * width))
        sys.stdout.write("\n")


def filter(items, periodicity="day", author=""):
    """Filter entries by periodicity and author."""
    bars = OrderedDict()
    for i in items:
        # Extract the day/month/year part of the date.
        p = i[0][:10]
        if periodicity == "month":
            p = i[0][:7]
        elif periodicity == "year":
            p = i[0][:4]

        # Filter by author.
        if author != "":
            if author not in i[1]:
                continue

        if p not in bars:
            bars[p] = 0
        bars[p] += 1

    return bars


def get_scores(items):
    """Compute normalized scores (0-1) for commit numbers."""
    vals = [items[i] for i in items]
    vals.append(0)

    xmin = min(vals)
    xmax = max(vals)

    # Normalize.
    return OrderedDict(
        (i, [items[i], normalize(items[i], xmin, xmax)]) for i in items)


def get_log(after, before, reverse):
    """Return the list of git log from the git log command."""
    # 2018-01-01 00:00:00|author@author.com
    args = ["git", "log", '--pretty=format:%ai|%ae']

    if after:
        args.append("--after=%s" % (after,))
    if before:
        args.append("--before=%s" % (before,))

    items = []
    for o in check_output(args, universal_newlines=True, shell=False) \
            .split("\n"):
        items.append(o.split("|"))

    if reverse:
        items.reverse()

    return items


def normalize(x, xmin, xmax):
    """Normalize a number to a 0-1 range given a min and max of its set."""
    return float(x - xmin) / float(xmax - xmin)


def main():
    """Commandline entry point."""
    p = argparse.ArgumentParser(description="git commit bars on the terminal")
    p.add_argument("-p", "--periodicity", action="store", dest="periodicity",
                   type=str, required=False, default="month",
                   help="day, month, year")

    p.add_argument("-u", "--author", action="store", dest="author",
                   type=str, required=False, default="",
                   help="filter by author's e-mail (substring)")

    p.add_argument("-a", "--after", action="store", dest="after",
                   type=str, required=False, default="",
                   help="after date (yyyy-mm-dd hh:mm)")

    p.add_argument("-b", "--before", action="store", dest="before",
                   type=str, required=False, default="",
                   help="before date (yyyy-mm-dd hh:mm)")

    p.add_argument("-r", "--reverse", action="store", dest="reverse",
                   type=bool, required=False, default=False,
                   help="reverse date order")

    args = p.parse_args()

    """Invoke the utility."""
    items = []
    try:
        items = get_log(args.after, args.before, args.reverse)
    except Exception as e:
        print("error running 'git log': %s" % (e,))
        return

    filtered = filter(items, args.periodicity, args.author)
    scores = get_scores(filtered)
    if scores:
        print("%d commits" % (sum([filtered[f] for f in filtered]),))
        print_bars(scores)
    else:
        print("No commits to plot")


if __name__ == "__main__":
    main()
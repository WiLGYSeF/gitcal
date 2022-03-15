# Gitcal

[![Build Status](https://www.travis-ci.com/WiLGYSeF/gitcal.svg?branch=master)](https://www.travis-ci.com/WiLGYSeF/gitcal)
[![codecov](https://codecov.io/gh/WiLGYSeF/gitcal/branch/master/graph/badge.svg?token=R4FFV0ZCGB)](https://codecov.io/gh/WiLGYSeF/gitcal)
[![PyPI version](https://badgen.net/pypi/v/gitcal)](https://pypi.org/project/gitcal/)

A python script to visualize when git commits were made in a repository in a calendar-like format.

# Examples

Display the number of commits in 2 hour blocks in 12 columns. A block with at least 4 commits is colored in green:

![sample gitcal usage](/docs/images/sample-gitcal.png)

---

An example of displaying two tables side-by-side, one with a border and different date range:

![sample gitcal usage](/docs/images/sample-gitcal-table-mix.png)

---

Compare commits with other members of a collaborative project:

![sample gitcal usage](/docs/images/sample-gitcal-all-users.png)

# Installation

```bash
pip install gitcal
```

# Displaying Multiple Tables

gitcal uses the `-T/--table` argument to display multiple tables.
A table is created based on the arguments on each side of `-T`, where the command below is used to create multiple tables:

```bash
gitcal -T -n "My Commits" --num --no-label -f "<my username>" -t 4 -T -n "Partner 1" -f "<partner 1>" -f "<also partner 1>"
#     ^   ^_______________________table 2________________________^    ^______________________table 3______________________^
#     |
# table 1
```

A sample result of the above command (below describes each table):

![sample gitcal usage](/docs/images/sample-gitcal-multiple-tables.png)

## Table 1

Since there are no arguments to the left of the first `-T`, the default table with all the daily commits is displayed per week.

## Table 2

To the right side of the first `-T`, we:

- set the table name with `-n`
- turn on commit counts with `--num` (underlines are used to distinguish number entries since there is no spacing on borderless tables)
- turn off labels with `--no-label` since the labels from the first table can be used instead
- filter for one user with `-f`
- set the color threshold `-t` to 4 commits

## Table 3

The second `-T` separates the second and third table options.
Note how table 3 only explicitly sets the table name and user filter, but the settings from the second table are carried over to the third table as well.
Most, but not all, settings are carried over between tables so they do not have to be repeated.

"""
Tests for AlgorithmM solver.
"""

import json
import unittest
import logging
from .algorithm_m import AlgorithmM, Header, Node

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def link_horizontally(nodes):
    if len(nodes) < 2:
        return

    root = nodes[0]

    for node in nodes[1:]:
        root.insert_left(node)


def _get_headers(iterable, primary, multiplicities=None):
    headers = {}

    if multiplicities is not None:
        for item, (lower, upper) in zip(iterable, multiplicities):
            bound = upper
            slack = upper - lower
            headers[item] = Header(name=item, primary=primary, slack=slack, bound=bound)

        return headers

    for item in iterable:
        headers[item] = Header(name=item, primary=primary)

    return headers


def get_headers(primary, multiplicities, secondary):
    return _get_headers(
        primary, primary=True, multiplicities=multiplicities
    ) | _get_headers(secondary, primary=False)


def add_headers(root, primary, secondary, headers):
    primary = [root] + [headers[header] for header in primary]
    secondary = [headers[header] for header in secondary]
    link_horizontally(primary)
    link_horizontally(secondary)
    root.secondary = secondary


def add_options(root, headers, options):
    for row in options:
        nodes = []

        for item in row:
            name, color = parse_item(item)
            header = headers[name]
            node = Node(row=row, name=item, header=header, color=color)
            header.insert_up(node)
            nodes.append(node)

        link_horizontally(nodes)


def generate_graph(primary_items, primary_multiplicities, secondary_items, options):
    root = Header(name="root")
    headers = get_headers(primary_items, primary_multiplicities, secondary_items)
    add_headers(root, primary_items, secondary_items, headers)
    add_options(root, headers, options)
    return root


def parse_item(item):
    if ":" in item:
        char, color = item.split(":")
        color = int(color)
    else:
        char = item
        color = 0

    return char, color


def convert_to_frozenset(solutions):
    solution_set = set()

    for solution in solutions:
        option_set = set()

        for option in solution:
            option_set.add(frozenset(option))

        solution_set.add(frozenset(option_set))

    return frozenset(solution_set)


class TestAlgorithmM(unittest.TestCase):
    """
    Tests for AlgorithmM solver.
    """

    def test_functional(self):
        """
        Perform functional testing.  Test case data and expected outputs can be
        very large, so they are stored separately as .json.
        """
        with open("functional_test_data.json", encoding="utf-8") as f_in:
            functional_test_data = json.load(f_in)

        for idx, test_data in enumerate(functional_test_data):
            logger.info("subtest: %s", idx)

            with self.subTest(idx):
                expected = test_data.pop("expected")
                root = generate_graph(**test_data)
                solutions = list(AlgorithmM(root).solutions())
                self.assertEqual(
                    convert_to_frozenset(solutions),
                    convert_to_frozenset(expected),
                )

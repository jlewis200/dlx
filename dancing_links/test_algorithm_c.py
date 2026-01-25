"""
Tests for AlgorithmC solver.
"""

import unittest
from .algorithm_c import AlgorithmC, Header, Node


def link_horizontally(nodes):
    if len(nodes) < 2:
        return

    root = nodes[0]

    for node in nodes[1:]:
        root.insert_left(node)


def _get_headers(iterable):
    headers = {}

    for item in iterable:
        headers[item] = Header(name=item)

    return headers


def get_headers(primary, secondary):
    return _get_headers(primary) | _get_headers(secondary)


def add_headers(root, primary, secondary, headers):
    primary = [root] + [headers[header] for header in primary]
    secondary = [headers[header] for header in secondary]
    link_horizontally(primary)
    link_horizontally(secondary)


def add_constraints(root, headers, constraints):
    for row in constraints:
        nodes = []

        for item in row:
            name, color = parse_item(item)
            header = headers[name]
            node = Node(row=row, name=item, header=header, color=color)
            header.insert_up(node)
            nodes.append(node)

        link_horizontally(nodes)


def generate_graph(primary, secondary, constraints):
    root = Header(name="root")
    headers = get_headers(primary, secondary)
    add_headers(root, primary, secondary, headers)
    add_constraints(root, headers, constraints)
    return root


def parse_item(item):
    if ":" in item:
        char, color = item.split(":")
        color = int(color, 0x10)
    else:
        char = item
        color = 0

    return char, color


class TestAlgorithmC(unittest.TestCase):
    """
    Tests for AlgorithmC solver.
    """

    def test_0(self):
        """
        Ensure the sovler handles the elementary exact color cover XCC problem
        The Art of Computer Programming:  7.2.2.1
        """
        root = generate_graph(
            primary=["p", "q", "r"],
            secondary=["x", "y"],
            constraints=[
                ["p", "q", "x", "y:A"],
                ["p", "r", "x:A", "y"],
                ["p", "x:B"],
                ["q", "x:A"],
                ["r", "y:B"],
            ],
        )

        solutions = []
        for solution in AlgorithmC(root).solutions():
            solutions.append(list(map(lambda x: x.row, solution)))

        self.assertEqual(
            solutions,
            [[["q", "x:A"], ["p", "r", "x:A", "y"]]],
        )

    def test_1(self):
        """
        Ensure the sovler handles the XCC problem from the DLX2 description
        https://www-cs-faculty.stanford.edu/~knuth/programs/dlx2.w
        """
        root = generate_graph(
            primary=["A", "B", "C"],
            secondary=["X", "Y"],
            constraints=[
                ["A", "B", "X:1", "Y:1"],
                ["A", "C", "X:2", "Y:2"],
                ["B", "X:2"],
                ["C", "Y:2"],
            ],
        )

        solutions = []
        for solution in AlgorithmC(root).solutions():
            solutions.append(list(map(lambda x: x.row, solution)))

        self.assertEqual(
            solutions,
            [[["A", "C", "X:2", "Y:2"], ["B", "X:2"]]],
        )

    def test_2(self):
        """
        Ensure the sovler handles the elementary problem described in
        The Art of Computer Programming:  7.2.2.1
        """
        root = generate_graph(
            primary=["a", "b", "c", "d", "e", "f", "g"],
            secondary=[],
            constraints=[
                ["c", "e"],
                ["a", "d", "g"],
                ["b", "c", "f"],
                ["a", "d", "f"],
                ["b", "g"],
                ["d", "e", "g"],
            ],
        )

        solutions = []
        for solution in AlgorithmC(root).solutions():
            solutions.append(list(map(lambda x: x.row, solution)))

        self.assertEqual(
            solutions,
            [[["a", "d", "f"], ["b", "g"], ["c", "e"]]],
        )

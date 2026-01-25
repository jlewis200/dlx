"""
Tests for AlgorithmX solver.
"""

import unittest
from .algorithm_x import AlgorithmX, Header, Node


class TestAlgorithmX(unittest.TestCase):
    """
    Tests for AlgorithmX solver.
    """

    def test_0(self):
        """
        Ensure the sovler handles the elementary problem described in
        The Art of Computer Programming:  7.2.2.1
        """
        root = Header(name="root")
        headers = {}

        for char in "abcdefg":
            header = Header(name=char)
            headers[char] = header
            root.insert_left(header)

        rows = ["ce", "adg", "bcf", "adf", "bg", "deg"]

        for row in rows:
            nodes = []

            for char in row:
                header = headers[char]
                node = Node(name=row, header=header)
                header.insert_up(node)
                nodes.append(node)

            node = nodes.pop(0)

            for other in nodes:
                node.insert_left(other)

        solutions = []
        for solution in AlgorithmX(root).solutions():
            solutions.append(list(map(lambda x: x.name, solution)))

        self.assertEqual(
            solutions,
            [["adf", "bg", "ce"]],
        )

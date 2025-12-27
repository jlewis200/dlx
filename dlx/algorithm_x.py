"""
Algorithm X constraint/exact-cover solver.
"""


class Node:
    """
    Node class for algorithm-x exact cover solver.
    """

    def __init__(
        self,
        header=None,
        name=None,
    ):
        self.u = self
        self.d = self
        self.l = self
        self.r = self
        self.header = header
        self.name = name

    def __repr__(self):
        return self.name

    def append_left(self, other):
        """
        Append other node to the left of self.
        """
        other.l = self.l
        other.r = self
        self.l.r = other
        self.l = other

    def append_right(self, other):
        """
        Append other node to the right of self.
        """
        other.r = self.r
        other.l = self
        self.r.l = other
        self.r = other

    def append_down(self, other):
        """
        Append other node under self.
        """
        other.d = self.d
        other.u = self
        self.d.u = other
        self.d = other

    def append_up(self, other):
        """
        Append other node above self.
        """
        other.u = self.u
        other.d = self
        self.u.d = other
        self.u = other


class Header(Node):
    """
    Header class to keep track of multiplicity of a column.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = self
        self.multiplicity = 0

    def append_down(self, other):
        """
        Append other node under self.
        """
        super().append_down(other)
        self.multiplicity += 1

    def append_up(self, other):
        """
        Append other node above self.
        """
        super().append_up(other)
        self.multiplicity += 1


class AlgorithmX:
    """
    Algorithm X solution generator class.
    """

    def __init__(self, root):
        self.root = root
        self.solution_stack = []

    def solutions(self):
        """
        Generate solutions to the exact cover problem.
        """
        if self.solved():
            yield self.get_solution()
            return

        min_column = self.get_min_column()
        self.cover(min_column)
        row = min_column.d

        while row != min_column:
            yield from self.enumerate_row(row)
            row = row.d

        self.uncover(min_column)

    def enumerate_row(self, row):
        """
        Assume row is in a solution.  Cover every column appearing in row and
        attempt to solve the reduced problem.
        """
        self.solution_stack.append(row)
        self.cover_columns(row)
        yield from self.solutions()
        self.uncover_columns(row)
        self.solution_stack.pop()

    def cover_columns(self, row):
        """
        Cover the columns appearing in row.
        """
        column = row.r

        while column != row:
            self.cover(column)
            column = column.r

    def uncover_columns(self, row):
        """
        Uncover the columns appearing in row.
        """
        column = row.l

        while column != row:
            self.uncover(column)
            column = column.l

    def cover(self, column):
        """
        Cover a column by removing it's header and hiding every row within the
        column.
        """
        header = column.header
        header.r.l = header.l
        header.l.r = header.r
        row = header.d

        while row != header:
            self.hide(row)
            row = row.d

    def hide(self, row):
        """
        Hide a row by removing up/down links for every node in the row.
        """
        node = row.r

        while node != row:
            node.d.u = node.u
            node.u.d = node.d
            node.header.multiplicity -= 1
            node = node.r

    def uncover(self, column):
        """
        Uncover a column by restoring the links to it.
        """
        header = column.header
        header.r.l = header
        header.l.r = header
        row = header.u

        while row != header:
            self.unhide(row)
            row = row.u

    def unhide(self, row):
        """
        Unhide a row by restoring the links to it.
        """
        node = row.l

        while node != row:
            node.d.u = node
            node.u.d = node
            node.header.multiplicity += 1
            node = node.l

    def get_min_column(self):
        """
        Find the column with the least possible choices.
        """
        min_column = None
        min_multiplicity = 2**64
        column = self.root.r

        while column != self.root:
            if column.multiplicity < min_multiplicity:
                min_column = column
                min_multiplicity = column.multiplicity

            column = column.r

        return min_column

    def solved(self):
        """
        Check if the problem is solved.
        """
        return self.root.r == self.root

    def get_solution(self):
        """
        Return a solution from the solution stack.
        """
        return self.solution_stack.copy()

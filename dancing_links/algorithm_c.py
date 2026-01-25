"""
Algorithm X constraint/exact-cover solver.
"""


class Node:
    """
    Node class for algorithm-x exact cover solver.
    """

    def __init__(self, header=None, name=None, row=None, color=0):
        self.u = self
        self.d = self
        self.l = self
        self.r = self
        self.header = header
        self.name = name
        self.row = row
        self.color = color

    def __repr__(self):
        return f"{self.row}|{self.name}" f"|{self.color}"

    def insert_left(self, other):
        """
        Append other node to the left of self.
        """
        other.l = self.l
        other.r = self
        self.l.r = other
        self.l = other

    def insert_right(self, other):
        """
        Append other node to the right of self.
        """
        other.r = self.r
        other.l = self
        self.r.l = other
        self.r = other

    def insert_down(self, other):
        """
        Append other node under self.
        """
        other.d = self.d
        other.u = self
        self.d.u = other
        self.d = other

    def insert_up(self, other):
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

    def insert_down(self, other):
        """
        Append other node under self.
        """
        super().insert_down(other)
        self.multiplicity += 1

    def insert_up(self, other):
        """
        Append other node above self.
        """
        super().insert_up(other)
        self.multiplicity += 1


class AlgorithmC:
    """
    Algorithm C solution generator class.
    """

    def __init__(self, root):
        self.root = root
        self.solution_stack = []

    def print_headers(self):
        node = self.root.r

        while node != self.root:
            print(node)
            node = node.r

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
        self.commit_columns(row)
        yield from self.solutions()
        self.uncommit_columns(row)
        self.solution_stack.pop()

    def commit_columns(self, row):
        """
        Cover the columns appearing in row.
        """
        column = row.r

        while column != row:
            self.commit(column)
            column = column.r

    def uncommit_columns(self, row):
        """
        Uncover the columns appearing in row.
        """
        column = row.l

        while column != row:
            self.uncommit(column)
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
            if node.color >= 0:
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
            if node.color >= 0:
                node.d.u = node
                node.u.d = node
                node.header.multiplicity += 1
            node = node.l

    def commit(self, node):
        if node.color == 0:
            self.cover(node)
        elif node.color > 0:
            self.purify(node)

    def purify(self, node):
        color = node.color
        header = node.header
        node = header.d

        while node != header:
            if node.color == color:
                node.color = -1
            else:
                self.hide(node)
            node = node.d

    def uncommit(self, node):
        if node.color == 0:
            self.uncover(node)
        elif node.color > 0:
            self.unpurify(node)

    def unpurify(self, node):
        color = node.color
        header = node.header
        node = header.u

        while node != header:
            if node.color < 0:
                node.color = color
            else:
                self.unhide(node)
            node = node.u

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

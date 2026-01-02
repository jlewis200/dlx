"""
Algorithm M constraint/exact-cover solver.
"""


class Node:
    """
    Node class for cover solver.
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
        return f"{self.row}|{self.name}|{self.color}"

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
    Header class to keep track of len of a column.
    """

    def __init__(self, *args, primary=True, slack=0, bound=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = self
        self.len = 0
        self.primary = primary
        self.slack = slack
        self.bound = bound
        self.secondary = None

    def insert_down(self, other):
        """
        Append other node under self.
        """
        super().insert_down(other)
        self.len += 1

    def insert_up(self, other):
        """
        Append other node above self.
        """
        super().insert_up(other)
        self.len += 1

    def __repr__(self):
        return (
            f"{self.row}|{self.name}|{self.color}|"
            f"{self.primary}|{self.len}|{self.slack}|{self.bound}"
        )


class AlgorithmM:
    """
    Algorithm M solution generator class.
    """

    def __init__(self, root):
        self.root = root
        self.solution_stack = []

    def print_headers(self):
        """
        Print debug information about the headers.
        """
        node = self.root.r

        while node != self.root:
            print(node)
            node = node.r

    def solutions(self):
        """
        Generate solutions to the multiple cover with color (MCC) problem.
        """
        if self.solved():
            yield self.get_solution()
            return

        min_column = self.get_min_column()
        first_tweak = min_column.d
        min_column.bound -= 1

        if min_column.bound == 0:
            self.cover(min_column)

        yield from self.enumerate_rows(min_column)
        yield from self.min_multiplicity_generator(min_column)

        self.untweak_helper(first_tweak)
        min_column.bound += 1

    def enumerate_rows(self, min_column):
        """
        Attempt to include each row in the solution.
        """
        row = min_column.d

        try:
            while row != min_column:
                self.tweak_helper(row)
                yield from self.include_row(row)
                row = row.d

        except ValueError:
            pass


    def min_multiplicity_generator(self, min_column):
        """
        If the slack & bound indicate that we have met the minimum multiplicity,
        eliminate this column (to satisfy it) and continue solving.
        """
        if min_column.bound < min_column.slack:
            min_column.l.r = min_column.r
            min_column.r.l = min_column.l
            yield from self.solutions()
            min_column.l.r = min_column
            min_column.r.l = min_column

    def tweak(self, row, hide=True):
        """
        Remove the row from consideration in future solutions.  When generating
        solutions the options which cover the primary items forms a set.  We
        don't care if the algorithm chooses options [A, B] vs [B, A].  This
        hiding optimization reduces those redundant choices by forcing an
        ordering through this option/row removal.
        """
        if hide:
            self.hide(row)

        header = row.header
        header.d = row.d
        row.d.u = header
        header.len -= 1

    def untweak(self, first_tweak, unhide=True):
        """
        Restore the 'tweaked' options by restoring the links.  This deviates
        from the Knuth implementation by keeping a reference to the first tweak
        in a function local variable in 'solutions()'.  This works here because
        of the recursive implementation.
        """
        header = first_tweak.header
        terminal_row = header.d
        header.d = first_tweak
        row = first_tweak
        prev_row = header

        while row != terminal_row:
            if unhide:
                self.unhide(row)

            row.u = prev_row
            prev_row = row
            row = row.d
            header.len += 1

        terminal_row.u = prev_row

    def tweak_helper(self, row):
        """
        This contains the majority of the logic from step 'M5 possibly tweak'.
        """
        header = row.header

        if (header.bound == 0) and (header.slack == 0):
            return

        if header.len <= (header.bound - header.slack):
            raise ValueError

        if header.bound != 0:
            self.tweak(row)

        elif header.bound == 0:
            self.tweak(row, hide=False)

    def untweak_helper(self, first_tweak):
        """
        This contains the majority of the logic from step 'M8 restore i'.
        """
        header = first_tweak.header

        if (header.bound == 0) and (header.slack == 0):
            self.uncover(header)

        else:
            if header.bound == 0:
                self.untweak(first_tweak, False)
            else:
                self.untweak(first_tweak)

    def include_row(self, row):
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
        Commit the columns appearing in row.
        """
        column = row.r

        while column != row:
            if column.header.primary:
                column.header.bound -= 1

                if column.header.bound == 0:
                    self.cover(column)

            else:
                self.commit(column)

            column = column.r

    def uncommit_columns(self, row):
        """
        Uncommit the columns appearing in row.
        """
        column = row.l

        while column != row:
            if column.header.primary:
                column.header.bound += 1

                if column.header.bound == 1:
                    self.uncover(column)

            else:
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
                node.header.len -= 1
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
                node.header.len += 1
            node = node.l

    def commit(self, node):
        """
        This is the color-compatible version of 'cover()'.  Color 0 indicates
        no color and the column can be covered.  If a color is specified, purify
        the column by removing all conflicting colors.
        """
        if node.color == 0:
            self.cover(node)
        elif node.color > 0:
            self.purify(node)

    def purify(self, node):
        """
        Purify the column by removing all 'other nodes' with colors conflicting with 'node'.
        """
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
        """
        Revert the effects of commit().
        """
        if node.color == 0:
            self.uncover(node)
        elif node.color > 0:
            self.unpurify(node)

    def unpurify(self, node):
        """
        Revert the effects of purify().
        """
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
        Find the column with the fewest choices.
        """
        min_column = None
        min_len = 2**64
        column = self.root.r

        while column != self.root:
            if column.len < min_len:
                min_column = column
                min_len = column.len

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
        solution = self.solution_stack.copy()
        return list(map(lambda x: x.row, solution))

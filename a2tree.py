"""
Assignment 2: Quadtree Compression

=== CSC148 Summer 2025 ===
Department of Mathematical and Computational Sciences,
University of Toronto Mississauga

=== Module Description ===
This module contains classes implementing the quadtree.
"""

from __future__ import annotations

import math
from copy import deepcopy
from typing import List, Tuple, Optional


# No other imports allowed


def mean_and_count(matrix: List[List[int]]) -> Tuple[float, int]:
    """
    Returns the average of the values in a 2D list
    Also returns the number of values in the list
    """
    total = 0
    count = 0
    for row in matrix:
        for v in row:
            total += v
            count += 1
    return total / count, count


def standard_deviation_and_mean(matrix: List[List[int]]) -> Tuple[float, float]:
    """
    Return the standard deviation and mean of the values in <matrix>

    https://en.wikipedia.org/wiki/Root-mean-square_deviation

    Note that the returned average is a float.
    It may need to be rounded to int when used.
    """
    avg, count = mean_and_count(matrix)
    total_square_error = 0
    for row in matrix:
        for v in row:
            total_square_error += ((v - avg) ** 2)
    return math.sqrt(total_square_error / count), avg


class QuadTreeNode:
    """
    Base class for a node in a quad tree
    """

    def __init__(self) -> None:
        pass

    def tree_size(self) -> int:
        raise NotImplementedError

    def convert_to_pixels(self, width: int, height: int) -> List[List[int]]:
        raise NotImplementedError

    def preorder(self) -> str:
        raise NotImplementedError


class QuadTreeNodeEmpty(QuadTreeNode):
    """
    An empty node represents an area with no pixels included
    """

    def __init__(self) -> None:
        super().__init__()

    def tree_size(self) -> int:
        """
        Note: An empty node still counts as 1 node in the quad tree
        """
        return 1

    def convert_to_pixels(self, width: int, height: int) -> List[List[int]]:
        """
        Convert to a properly formatted empty list
        """
        # Note: Normally, this method should return an empty list or a list of
        # empty lists. However, when the tree is mirrored, this returned list
        # might not be empty and may contain the value 255 in it. This will
        # cause the decompressed image to have unexpected white pixels.
        # You may ignore this caveat for the purpose of this assignment.
        return [[255] * width for _ in range(height)]

    def preorder(self) -> str:
        """
        The letter E represents an empty node
        """
        return 'E'


class QuadTreeNodeLeaf(QuadTreeNode):
    """
    A leaf node in the quad tree could be a single pixel or an area in which
    all pixels have the same colour (indicated by self.value).
    """

    value: int  # the colour value of the node

    def __init__(self, value: int) -> None:
        super().__init__()
        assert isinstance(value, int)
        self.value = value

    def tree_size(self) -> int:
        """
        Return the size of the subtree rooted at this node
        """
        return 1

    def convert_to_pixels(self, width: int, height: int) -> List[List[int]]:
        """
        Return the pixels represented by this node as a 2D list

        >>> sample_leaf = QuadTreeNodeLeaf(5)
        >>> sample_leaf.convert_to_pixels(2, 2)
        [[5, 5], [5, 5]]
        """
        lst = []
        for j in range(height):
            r = []
            for k in range(width):
                r.append(self.value)
            lst.append(r)
        return lst

    def preorder(self) -> str:
        """
        A leaf node is represented by an integer value in the preorder string
        """
        return str(self.value)


class QuadTreeNodeInternal(QuadTreeNode):
    """
    An internal node is a non-leaf node, which represents an area that will be
    further divided into quadrants (self.children).

    The four quadrants must be ordered in the following way in self.children:
    bottom-left, bottom-right, top-left, top-right

    (List indices increase from left to right, bottom to top)

    Representation Invariant:
    - len(self.children) == 4
    """
    children: List[Optional[QuadTreeNode]]

    def __init__(self) -> None:
        """
        Order of children: bottom-left, bottom-right, top-left, top-right
        """
        super().__init__()

        # Length of self.children must be always 4.
        self.children = [None, None, None, None]

    def tree_size(self) -> int:
        """
        The size of the subtree rooted at this node.

        This method returns the number of nodes that are in this subtree,
        including the root node.
        """
        sums = 1
        for j in self.children:
            if j is not None:
                sums = sums + j.tree_size()
        return sums

    def convert_to_pixels(self, width: int, height: int) -> List[List[int]]:
        """
        Return the pixels represented by this node as a 2D list.

        You'll need to recursively get the pixels for the quadrants and
        combine them together.

        Make sure you get the sizes (width/height) of the quadrants correct!
        Read the docstring for split_quadrants() for more info.
        """
        b_h = height // 2
        l_w = width // 2
        t_h = height - b_h
        r_w = width - l_w

        a, b = self.children[0], self.children[1]
        bl = a.convert_to_pixels(l_w, b_h)
        br = b.convert_to_pixels(r_w, b_h)
        c, d = self.children[2], self.children[3]
        tl = c.convert_to_pixels(l_w, t_h)
        tr = d.convert_to_pixels(r_w, t_h)

        lst_1 = []
        lst_2 = []
        ans = []
        if isinstance(width, int) and isinstance(height, int):
            ltl = len(tl)
            for i in range(0, ltl):
                temp = []
                for v in tl[i]:
                    temp.append(v)
                for v in tr[i]:
                    temp.append(v)
                lst_1.append(temp)

            lbl = len(bl)
            for i in range(0, lbl):
                temp2 = []
                for v in bl[i]:
                    temp2.append(v)
                for v in br[i]:
                    temp2.append(v)
                lst_2.append(temp2)
        else:
            raise ValueError("width and height must be integers")

        for row in lst_2:
            ans.append(row)
        for row in lst_1:
            ans.append(row)

        return ans

    def preorder(self) -> str:
        """
        Return a string representing the preorder traversal or the tree rooted
        at this node. See the docstring of the preorder() method in the
        QuadTree class for more details.

        An internal node is represented by an empty string in the preorder
        string.
        """
        lst = []
        temp = ','
        for k in self.children:
            x = k.preorder()
            lst.append(x)
        final = temp + ','.join(lst)
        return final

    def restore_from_preorder(self, lst: List[str], start: int) -> int:
        """
        Restore subtree from preorder list <lst>, starting at index <start>
        Return the number of entries used in the list to restore this subtree
        """

        # This assert will help you find errors.
        # Since this is an internal node, the first entry to restore should
        # be an empty string
        assert lst[start] == ''
        fin = 1
        x = start + fin
        count = 0
        holder = 1
        if isinstance(start, int):
            if start < 0:
                raise ValueError("Invalid Input, make start positive int")
            elif start >= 0:
                while count < 4:
                    curr = lst[x]
                    if curr == '':
                        temp = QuadTreeNodeInternal()
                        self.children[count] = temp
                        consumed = temp.restore_from_preorder(lst, x)
                        fin = fin + consumed
                        x = x + consumed

                    elif curr == 'E':
                        self.children[count] = QuadTreeNodeEmpty()
                        x = x + holder
                        fin = fin + holder

                    else:  # all else fails
                        lf = int(curr)
                        self.children[count] = QuadTreeNodeLeaf(lf)
                        x += holder
                        fin += holder
                    count += 1

        return fin

    def mirror(self) -> None:
        """
        Mirror the bottom half of the image represented by this tree over
        the top half

        Example:
            Original Image
            1 2
            3 4

            Mirrored Image
            3 4 (this row is flipped upside down)
            3 4

        See the assignment handout for a visual example.
        """
        a, b, c, d = 0, 1, 2, 3
        f1 = self.children[a]
        f2 = self.children[b]
        self.children[c] = self._helper_flipper(f1)
        self.children[d] = self._helper_flipper(f2)

    def _helper_flipper(self, node: QuadTreeNode) -> QuadTreeNode:
        """
        Returns a deep copy of <node> that is flipped in the vertical direction.
        """
        z = 0
        a, b, c, d = z, 1, 2, 3
        if isinstance(node, QuadTreeNodeEmpty):
            return QuadTreeNodeEmpty()
        if isinstance(node, QuadTreeNodeLeaf):
            return QuadTreeNodeLeaf(node.value)
        xl, xr, yl, yr = node.children
        fin = QuadTreeNodeInternal()

        if xl is None or xr is None or yl is None or yr is None:
            raise ValueError("Input is Invalid.")
        else:
            fin.children[a], fin.children[b] = self._helper_flipper(yl), self._helper_flipper(yr)
            fin.children[c] = self._helper_flipper(xl)
            fin.children[d] = self._helper_flipper(xr)
        return fin


class QuadTree:
    """
    The class for the overall quadtree
    """

    loss_level: float
    height: int
    width: int
    root: Optional[QuadTreeNode]  # safe to assume root is an internal node

    def __init__(self, loss_level: int = 0) -> None:
        """
        Precondition: the size of <pixels> is at least 1x1
        """
        self.loss_level = float(loss_level)
        self.height = -1
        self.width = -1
        self.root = None

    def build_quad_tree(self, pixels: List[List[int]],
                        mirror: bool = False) -> None:
        """
        Build a quad tree representing all pixels in <pixels>
        and assign its root to self.root

        <mirror> indicates whether the compressed image should be mirrored.
        See the assignment handout for examples of how mirroring works.
        """
        self.height = len(pixels)
        self.width = len(pixels[0])
        self.root = self._build_tree_helper(pixels)
        if mirror:
            self.root.mirror()
        return

    def _build_tree_helper(self, pixels: List[List[int]]) -> QuadTreeNode:
        """
        Build a quad tree representing all pixels in <pixels>
        and return the root

        Note that self.loss_level should affect the building of the tree.
        This method is where the compression happens.

        IMPORTANT: the condition for compressing a quadrant is the standard
        deviation being __LESS THAN OR EQUAL TO__ the loss level. You must
        implement this condition exactly; otherwise, you could fail some
        test cases unexpectedly.
        """
        y = len(pixels)
        pos = 0
        if y == pos:
            return QuadTreeNodeEmpty()
        x = len(pixels[0])
        if x == pos:
            return QuadTreeNodeEmpty()
        if y == 1 and x == 1:
            return QuadTreeNodeLeaf(int(pixels[0][0]))

        sd, avg = standard_deviation_and_mean(pixels)
        l_l = self.loss_level
        if sd <= l_l:
            m = int(round(avg))
            return QuadTreeNodeLeaf(m)
        else:
            a, b, c, d = self._split_quadrants(pixels)
            n = QuadTreeNodeInternal()
            temp1, temp2 = self._build_tree_helper(a), self._build_tree_helper(b)
            n.children[0] = temp1
            n.children[1] = temp2
            temp3, temp4 = self._build_tree_helper(c), self._build_tree_helper(d)
            n.children[2] = temp3
            n.children[3] = temp4
        return n


    @staticmethod
    def _split_quadrants(pixels: List[List[int]]) -> List[List[List[int]]]:
        """
        Precondition: size of <pixels> is at least 1x1
        Returns a list of four lists of lists, correspoding to the quadrants in
        the following order: bottom-left, bottom-right, top-left, top-right

        IMPORTANT: when dividing an odd number of entries, the smaller half
        must be the left half or the bottom half, i.e., the half with lower
        indices.

        Postcondition: the size of the returned list must be 4

        >>> example = QuadTree(0)
        >>> example._split_quadrants([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        [[[1]], [[2, 3]], [[4], [7]], [[5, 6], [8, 9]]]
        """
        h = len(pixels)
        w = 0
        pos = 0
        if h > pos:
            w = len(pixels[0])

        a = w // 2
        b = h // 2
        x = pixels[:b]
        y = pixels[b:]
        x_l, x_r = [], []
        y_l, y_r = [], []
        for i in x:
            temp = i[:a]
            x_l.append(temp)
            temp2 = i[a:]
            x_r.append(temp2)

        for j in y:
            c1 = j[:a]
            y_l.append(c1)
            c2 = j[a:]
            y_r.append(c2)

        final = [x_l, x_r, y_l, y_r]
        return final

    def tree_size(self) -> int:
        """
        Return the number of nodes in the tree, including all Empty, Leaf, and
        Internal nodes.
        """
        return self.root.tree_size()

    def convert_to_pixels(self) -> List[List[int]]:
        """
        Return the pixels represented by this tree as a 2D matrix
        """
        return self.root.convert_to_pixels(self.width, self.height)

    def preorder(self) -> str:
        """
        return a string representing the preorder traversal of the quadtree.
        The string is a series of entries separated by comma (,).
        Each entry could be one of the following:
        - empty string '': represents a QuadTreeNodeInternal
        - string of an integer value such as '5': represents a QuadTreeNodeLeaf
        - string 'E': represents a QuadTreeNodeEmpty

        For example, consider the following tree with a root and its 4 children
                __      Root       __
              /      |       |        \
            Empty  Leaf(5), Leaf(8), Empty

        preorder() of this tree should return exactly this string: ",E,5,8,E"

        (Note the empty-string entry before the first comma)
        """
        return self.root.preorder()

    @staticmethod
    def restore_from_preorder(lst: List[str],
                              width: int, height: int) -> QuadTree:
        """
        Restore the quad tree from the preorder list <lst>
        The preorder list <lst> is the preorder string split by comma

        Precondition: the root of the tree must be an internal node (non-leaf)
        """
        tree = QuadTree()
        tree.width = width
        tree.height = height
        tree.root = QuadTreeNodeInternal()
        tree.root.restore_from_preorder(lst, 0)
        return tree


def maximum_loss(original: QuadTreeNode, compressed: QuadTreeNode) -> float:
    """
    Given an uncompressed image as a quad tree and the compressed version,
    return the maximum loss across all compressed quadrants.

    Precondition: original.tree_size() >= compressed.tree_size()

    Note: original, compressed are the root nodes (QuadTreeNode) of the
    trees, *not* QuadTree objects

    >>> pixels = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    >>> orig, comp = QuadTree(0), QuadTree(2)
    >>> orig.build_quad_tree(pixels)
    >>> comp.build_quad_tree(pixels)
    >>> maximum_loss(orig.root, comp.root)
    1.5811388300841898
    """

    def _std_eq(lst: List[int]) -> float:
        """
        Calculates the standard deviation of a list of integers and Returns it.
        """
        holder = 2
        end = 0.0
        if isinstance(lst, list) and len(lst) > 0:
            if lst is True:
                fin = 0
                x = len(lst)
                summ = sum(lst)
                mew = summ / len(lst)
                for i in lst:
                    diff = (i - mew)
                    fin = fin + diff ** holder
                return math.sqrt(fin / x)
            else:
                return end
        else:
            raise ValueError("Invalid input")

    def _helper_collect_values(node: QuadTreeNode) -> List[int]:
        """ Helper function to collect values from the node"""
        if isinstance(node, QuadTreeNodeEmpty):
            return []
        elif isinstance(node, QuadTreeNodeLeaf):
            temp = node.value
            return [temp]
        v: List[int] = []
        for i in node.children:
            curr = _helper_collect_values(i)
            v.extend(curr)
        return v

    def _helper_max(x: QuadTreeNode, t: QuadTreeNode) -> float:
        """
        Helper functino that takes two nodes <x> and <t> and Return the maximum loss between them
        """
        if isinstance(t, QuadTreeNodeLeaf) or isinstance(t, QuadTreeNodeEmpty):
            return _std_eq(_helper_collect_values(x))

        quality = 0.0
        count = 0
        while count < 4:
            if isinstance(x, QuadTreeNodeInternal):
                xc = x.children[count]
            else:
                xc = x
            temp = t.children[count]
            comp = _helper_max(xc, temp)
            quality = max(0.0, comp)
            count += 1
        return quality

    return _helper_max(original, compressed)


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'doctest', 'math', 'copy', '__future__'
        ],
        'disable': ['E9955', 'E9951']
    })


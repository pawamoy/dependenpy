"""Tests for algorithms."""

import pytest

from dependenpy import algorithms, structures


@pytest.fixture()
def full_matrix() -> algorithms.DsmMatrix:
    """A default matrix to test with.

    Returns:
        algorithms.DsmMatrix: _description_
    """
    matrix = structures.Matrix.cast(
        ["a", "b", "c", "d"],
        [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, 16],
        ],
    )
    return algorithms.DsmMatrix.create(matrix)


@pytest.fixture()
def sparse_matrix() -> algorithms.DsmMatrix:
    """A default sparse matrix to test with.

    Returns:
        algorithms.DsmMatrix: _description_
    """
    matrix = structures.Matrix.cast(
        ["a", "b", "c", "d"],
        [
            [1, 2, 0, 4],
            [0, 0, 0, 0],
            [9, 10, 0, 12],
            [13, 14, 0, 16],
        ],
    )
    return algorithms.DsmMatrix.create(matrix)


@pytest.fixture()
def complex_matrix() -> algorithms.DsmMatrix:
    """A default sparse matrix to test with.

    Returns:
        algorithms.DsmMatrix: _description_
    """
    matrix = structures.Matrix.cast(
        ["a", "b", "c", "d", "e", "f", "g"],
        [
            [0, 0, 2, 0, 0, 0, 0],
            [0, 0, 1, 3, 0, 0, 0],
            [4, 0, 0, 0, 5, 0, 0],
            [6, 0, 0, 0, 0, 0, 7],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 4, 0, 8],
            [0, 9, 5, 0, 0, 0, 0],
        ],
    )
    return algorithms.DsmMatrix.create(matrix)


@pytest.fixture()
def complex_matrix_done() -> algorithms.DsmMatrix:
    """The complex matrix, sequenced.

    Returns:
        algorithms.DsmMatrix: _description_
    """
    matrix = structures.Matrix.cast(
        ["f", "b", "d", "g", "c", "a", "e"],
        [
            [0, 0, 0, 8, 1, 0, 4],
            [0, 0, 3, 0, 1, 0, 0],
            [0, 0, 0, 7, 0, 6, 0],
            [0, 9, 0, 0, 5, 0, 0],
            [0, 0, 0, 0, 0, 4, 5],
            [0, 0, 0, 0, 2, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ],
    )
    return algorithms.DsmMatrix.create(matrix)


@pytest.fixture()
def cluster_matrix() -> algorithms.DsmMatrix:
    """The complex matrix, sequenced.

    Returns:
        algorithms.DsmMatrix: _description_
    """
    matrix = structures.Matrix.cast(
        ["a", "b", "c", "d", "e", "f", "g"],
        [
            [0, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 1],
            [0, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 1, 0, 1, 0],
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0, 0, 0],
        ],
    )
    return algorithms.DsmMatrix.create(matrix)


def test_switch_elements(full_matrix: algorithms.DsmMatrix):  # noqa: WPS442
    """Check that switching elements gives expected result.

    Args:
        full_matrix (algorithms.DsmMatrix): _description_
    """
    actual = full_matrix.switch_elements(0, 2)
    assert actual.keys == ["c", "b", "a", "d"]
    assert actual.data == [[11, 10, 9, 12], [7, 6, 5, 8], [3, 2, 1, 4], [15, 14, 13, 16]]


def test_switch_elements_twice_is_null_operation(full_matrix: algorithms.DsmMatrix):  # noqa: WPS442
    """Check that switching elements twice is reverting to original matrix.

    Args:
        full_matrix (algorithms.DsmMatrix): _description_
    """
    actual = full_matrix.switch_elements(0, 2)
    actual = actual.switch_elements(0, 2)
    assert actual.keys == full_matrix.keys
    assert actual.data == full_matrix.data


def test_element_to_front(full_matrix: algorithms.DsmMatrix):  # noqa: WPS442
    """Check that element_to_front works as expected.

    Args:
        full_matrix (algorithms.DsmMatrix): the matrix to test with
    """
    actual = full_matrix.element_to_front(2)
    assert actual.front == 1
    assert actual.keys == ["c", "b", "a", "d"]

    actual = actual.element_to_front(2)
    assert actual.front == 2
    assert actual.keys == ["c", "a", "b", "d"]


def test_element_to_back(full_matrix: algorithms.DsmMatrix):  # noqa: WPS442
    """Check that element_to_front works as expected.

    Args:
        full_matrix (algorithms.DsmMatrix): the matrix to test with
    """
    actual = full_matrix.element_to_back(1)
    assert actual.back == actual.rank - 1
    assert actual.keys == ["a", "d", "c", "b"]

    actual = actual.element_to_back(1)
    assert actual.back == actual.rank - 2
    assert actual.keys == ["a", "c", "d", "b"]


def test_has_inputs(sparse_matrix):
    sparse_matrix.print()
    assert not sparse_matrix.has_inputs(1)
    assert sparse_matrix.has_inputs(2)


def test_has_outputs(sparse_matrix):
    sparse_matrix.print()
    assert sparse_matrix.has_outputs(1)
    assert not sparse_matrix.has_outputs(2)


def test_sequence(complex_matrix, complex_matrix_done):
    complex_matrix.print(zero=".")
    result = complex_matrix.sequence()
    result.print(zero=".")
    complex_matrix_done.print(zero=".")
    # assert False


def test_reachability(cluster_matrix):
    levels = cluster_matrix.get_levels()
    print(levels)
    levels = [x for xs in levels for x in xs]
    print(levels)
    cluster_matrix.print(zero=".")
    cluster_matrix.levelize().print(zero=".")
    assert False

import tsp

from math import sqrt

def test_all_pairs():
    '''make sure we actually generate all pairs'''
    expected=[(0,0),(0,1),(1,0),(1,1),(0,2),(2,0),(1,2),(2,1),(2,2)]
    pairs=list(tsp.all_pairs(3))
    assert len(expected) == len(pairs)
    for pair in expected:
        assert pair in pairs

def test_reversed_sections():
    expected=[[2,1,3],[3,1,2],[3,2,1],[1,3,2],[2,3,1]]
    rev=list(tsp.reversed_sections([1,2,3]))
    assert len(expected) == len(rev)
    for tour in expected:
        assert tour in rev

def test_swapped_cities():
    expected=[[2,1,3],[3,2,1],[1,3,2]]
    swapped=list(tsp.swapped_cities([1,2,3]))
    assert len(expected) == len(swapped)
    for tour in expected:
        assert tour in swapped

def test_cartesian_matrix():
    coords=[(0,0),(0,1),(1,0),(1,1)]
    matrix=tsp.cartesian_matrix(coords)
    
    assert 16 == len(matrix)
    
    assert matrix[(0,0)] == 0
    assert matrix[(1,1)] == 0
    assert matrix[(2,2)] == 0
    assert matrix[(3,3)] == 0
    
    assert matrix[(0,1)] == 1
    assert matrix[(1,0)] == 1
    assert matrix[(0,2)] == 1
    assert matrix[(2,0)] == 1
    assert matrix[(0,3)] == sqrt(2)
    assert matrix[(3,0)] == sqrt(2)
    
    assert matrix[(1,2)] == sqrt(2)
    assert matrix[(2,1)] == sqrt(2)
    assert matrix[(1,3)] == 1
    assert matrix[(3,1)] == 1
    
    assert matrix[(2,3)] == 1
    assert matrix[(3,2)] == 1

def test_read_coords():
    coord_file="""0.0,0.0\n0,1\n1,0.0\n1.0,1.0""".split()
    coords=tsp.read_coords(coord_file)
    
    assert 4 == len(coords)
    assert [(0.0,0.0),(0.0,1.0),(1.0,0.0),(1.0,1.0)] == coords

def test_tour_length():
    coords=[(0,0),(0,1),(1,0),(1,1)]
    matrix=tsp.cartesian_matrix(coords)
    
    assert 2 == tsp.tour_length(matrix,[0,1])
    assert 2 == tsp.tour_length(matrix,[0,2])
    
    assert (1+sqrt(2)+1) == tsp.tour_length(matrix,[0,1,2])
    assert (1+sqrt(2)+1+sqrt(2)) == tsp.tour_length(matrix,[0,1,2,3])
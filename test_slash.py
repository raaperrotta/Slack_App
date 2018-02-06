from math import inf
import slash

def test_calc_table():
    points, player_max = slash.calc_table('100')
    assert points == [[50], [34], [25], [20], [17], [15], [13], [12], [10]]
    assert player_max is inf

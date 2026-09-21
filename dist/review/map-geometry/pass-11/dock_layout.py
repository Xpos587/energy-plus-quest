"""Dock bay boundaries, shared by the source repair and alignment check."""
DOORS = [-19.25, -17.15, -15.05, -12.95, -10.85, -8.75]
BOUNDARIES = [DOORS[0] - (DOORS[1] - DOORS[0]) / 2]
BOUNDARIES += [(left + right) / 2 for left, right in zip(DOORS, DOORS[1:])]
BOUNDARIES += [DOORS[-1] + (DOORS[-1] - DOORS[-2]) / 2]

if __name__ == '__main__':
    assert len(BOUNDARIES) == len(DOORS) + 1
    for index, door in enumerate(DOORS):
        left, right = BOUNDARIES[index:index + 2]
        assert left < door < right
        assert abs((left + right) / 2 - door) < 1e-8
        assert min(abs(door - line) for line in BOUNDARIES) > 1
    print('PASS: six gates centered in six bays; seven shared boundary lines, no centerline.')

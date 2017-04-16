import numpy


L90 = numpy.array([[0, 1], [-1, 0]]).astype(numpy.float32)
R90 = numpy.array([[0, -1], [1, 0]]).astype(numpy.float32)


def row_norms(matrix):
    return numpy.sqrt(numpy.sum(matrix * matrix, axis=1, keepdims=True))


def scale_rows(scalar, matrix):
    return matrix * (scalar / row_norms(matrix))


def rotation(alpha):
    """
    Counter clockwise rotation matrix of a vector around the origin
    :param alpha: degree, in radians, of the rotation
    """
    c = numpy.cos(alpha)
    s = numpy.sin(alpha)
    return numpy.array([[c, s], [-s, c]])


def straight(velocity, dt):
    """
    Return a function that calculates new positions given velocity and time delta.
    :param velocity: scalar velocity
    :param dt: time delta
    :return: function that takes positions and directions, returning new positions
    """
    distance = velocity * dt

    def run(positions, directions):
        return positions + scale_rows(distance, directions)

    return run


def turn(velocity, turning_radius, dt):
    """
    Return a function that calculates new positions and directions given velocity, turning radius and time delta.
    A positive turn radius is a right turn, while a negative is a left turn.
    :param velocity: scalar velocity
    :param turning_radius: scalar turning radius
    :param dt: scalar time delta
    :return: function that takes positions and directions and returns updates positions and directions
    """
    angle = velocity * dt / turning_radius

    rotation_matrix = rotation(angle)
    offset_matrix = L90 - numpy.dot(L90, rotation_matrix)

    def run(positions, directions):
        new_positions = positions + numpy.dot(scale_rows(turning_radius, directions), offset_matrix)
        new_directions = numpy.dot(directions, rotation_matrix)
        return new_positions, new_directions

    return run


class GameState():
    borders = None
    positions = None
    directions = None
    velocity = None

    def __init__(self, width, height, players, velocity):
        self.borders = numpy.array([width, height], dtype=numpy.float32)
        self.positions = numpy.mod(numpy.random.random((players, 2)) * self.borders, self.borders).astype(numpy.float32)
        self.directions = (numpy.random.randn(players, 2)*40).astype(numpy.float32)
        self.velocity = velocity
        self.directions = scale_rows(self.velocity, self.directions)

    def wrap(self):
        self.positions = numpy.mod(self.positions, self.borders)

    def straight(self, ixs, dt):
        update = straight(self.velocity, dt)
        self.positions[ixs, :] = update(self.positions[ixs, :], self.directions[ixs, :])

    def turn(self, ixs, turning_radius, dt):
        update = turn(self.velocity, turning_radius, dt)
        self.positions[ixs, :], self.directions[ixs, :] = update(
            self.positions[ixs, :],
            self.directions[ixs, :]
        )

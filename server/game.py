import numpy

# def rotatation(rads):
#     c = numpy.cos(rads)
#     s = numpy.sin(rads)
#     return nump.array([[c, -s],[s, c]])
#
# def rotate(matrix, rads):
#     return numpy.dot(rotation(rads), matrix)

l90 = numpy.array([[0, -1],[1, 0]]).astype(numpy.float32)
r90 = numpy.array([[0, 1],[-1, 0]]).astype(numpy.float32)

def straight(positions, velocities, dt):
    return positions + velocities * dt

def rotate_left(positions, vnorm, velocities, dt, turning_radius):
    rads = vnorm / dt
    s = numpy.sin(rads) + 1
    c = numpy.cos(rads)
    r = numpy.array([[-s, -c], [c, -s]])
    return positions + numpy.dot(r, velocities)

def rownorms(matrix):
    return numpy.sum(matrix * matrix, 1)

def left_90(matrix):
    return numpy.dot(l90, matrix)

def right_90(matrix):
    return numpy.dot(r90, matrix)

class GameState():
    borders = None
    positions = None
    directions = None
    velocity = None

    def __init__(self, width, height, players, velocity):
        self.borders = numpy.array([width, height], dtype=numpy.float32)
        self.positions = numpy.mod(numpy.random.random((players,2)) * self.borders, self.borders).astype(numpy.float32)
        self.directions = (numpy.random.randn(players,2)*40).astype(numpy.float32)
        self.directions = self.directions / numpy.sqrt(rownorms(self.directions))
        self.velocity = velocity

    def wrap(self):
        self.positions = numpy.mod(self.positions, self.borders)

    def straight(self, ixs, dt):
        self.positions[ixs,:] = self.positions[ixs,:] + self.velocity * self.directions[ixs, :] * dt

    def rotate_left(self, ixs, turning_radius, dt):
        rads = (self.velocity * dt) / turning_radius
        s = numpy.sin(rads)
        c = numpy.cos(rads)
        mov = numpy.array([[-s-1, -c], [c, -s-1]]).astype(numpy.float32)
        rot = numpy.array([[c, -s], [s, c]]).astype(numpy.float32)
        self.positions[ixs, :] += numpy.dot(mov, self.directions[ixs, :].T * turning_radius).T
        self.directions[ixs, :] = numpy.dot(rot, self.directions[ixs, :].T).T

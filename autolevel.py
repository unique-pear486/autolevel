from __future__ import division
import math
import random
import numpy as np


DIRECTIONS = (np.array((0, 1)),
              np.array((1, 0)),
              np.array((0, -1)),
              np.array((-1, 0)))     # Cardinal directions
WINDINGNESS = 20        # 1/WINDINESS chance of turning without being forced


class Room(object):
    """A room object. Occupys cells x1 to x2-1, y1 to y2-1"""
    def __init__(self, x1, y1, x2, y2):
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)

    @property
    def centre(self):
        return ((self.x1 + self.x2)/2, (self.y1 + self.y2)/2)

    @property
    def area(self):
        return ((self.x2 - self.x1) * (self.y2 - self.y1))

    @property
    def coords(self):
        return (self.x1, self.y1, self.x2, self.y2)


def generate_dungeon(x, y, height, attempts, **options):
    """Generate a dungeon x by y cells, height cells high"""
    if (x % 2 != 1) or (y % 2 != 1):
        yield ValueError("Sizes must be odd")
    terrain = np.zeros([x, y], dtype=int)
    rooms = generate_rooms(x, y, 200)
    yield rooms
    region = 1
    for room in rooms:
        carve(room, terrain, region)
        region += 1
    for i in range(1, terrain.shape[0], 2):
        for j in range(1, terrain.shape[1], 2):
            if terrain[i, j] == 0:
                grow_maze(terrain, (i, j), region)
                region += 1
    yield terrain
    # terr_temp = np.zeros([x+2, y+2], dtype=int)
    # terr_temp[1:-1, 1:-1] = terrain
    N_walls = np.logical_and(terrain == 0, np.roll(terrain, 1, 0) > 0)
    S_walls = np.logical_and(terrain == 0, np.roll(terrain, -1, 0) > 0)
    E_walls = np.logical_and(terrain == 0, np.roll(terrain, 1, 1) > 0)
    W_walls = np.logical_and(terrain == 0, np.roll(terrain, -1, 1) > 0)
    yield terrain + 2*N_walls + 2*S_walls + 2*E_walls + 2*W_walls


def generate_rooms(x, y, tries):
    """Generate dungeon rooms x by y cells"""
    rooms = []
    maxsize = min(x, y) // 2
    for i in range(0, tries):
        x1 = random.randint(1, x // 2)*2 + 1
        y1 = random.randint(1, y // 2)*2 + 1
        width = int(random.random()**2 * maxsize) + 4
        height = int(random.random()**2 * maxsize) + 4
        ratio = abs(width / height)
        if ratio < 0.1 or ratio > 10:
            continue
        x2 = x1 + width
        y2 = y1 + width
        if x2 >= x or y2 >= y:
            continue
        room = Room(x1, y1, x2, y2)
        if any(intersects(room, r) for r in rooms):
            continue
        else:
            rooms.append(room)
    return rooms


def intersects(room1, room2):
    """Check whether the two rectangular rooms intersect"""
    x_int = ((room2.x1 < room1.x2 + 1) and (room2.x2 + 1 > room1.x1))
    y_int = ((room2.y1 < room1.y2 + 1) and (room2.y2 + 1 > room1.y1))
    if x_int and y_int:
        return True
    else:
        return False


def carve(area, terrain, n=1):
    if hasattr(area, "x1"):
        for i in range(area.x1, area.x2):
            for j in range(area.y1, area.y2):
                terrain[i, j] = n
    else:
        terrain[tuple(area)] = n


def grow_maze(terrain, start, region):
    cells = [start]
    previous_direction = random.sample(DIRECTIONS, 1)[0]
    while cells:
        cell = cells[-1]
        open_cells = []
        # Search for direcions we can carve
        for direction in DIRECTIONS:
            if can_carve(cell, direction, terrain):
                open_cells.append(direction)

        # Depending on Winding factor, prefer previous direction
        if open_cells:
            if (tuple(previous_direction) in [tuple(i) for i in open_cells] and
                    random.random() > 1/WINDINGNESS):   # tuple for np wierdnes
                direction = previous_direction
            else:
                direction = random.sample(open_cells, 1)[0]
            carve(cell + direction, terrain, region)
            carve(cell + direction*2, terrain, region)
            cells.append(cell + direction*2)
        else:
            cells.pop()
    return terrain


def can_carve(cell, direction, terrain):
    """Check if there are any walls or the boundary in the way"""
    (x, y) = cell + direction*3
    if x < 0 or x >= terrain.shape[0]:
        return False
    if y < 0 or y >= terrain.shape[1]:
        return False
    if terrain[tuple(cell + direction*2)] == 0:
        return True
    return False


class Triangle(object):
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.circumcircle = self._circumcircle()

    def __iter__(self):
        line1 = Line(self.p1, self.p2)
        line2 = Line(self.p2, self.p3)
        line3 = Line(self.p3, self.p1)
        return iter([line1, line2, line3])

    def in_circumcircle(self, point):
        """Determine if a point is in the triangle's circumcircle"""
        x, y = point
        (cx, cy), cr = self.circumcircle
        r2 = (x - cx)**2 + (y - cy)**2
        if r2 < cr**2:
            return True
        return False

    def _circumcircle(self):
        """Return the circumcircle centre and radius"""
        ax, ay = self.p1
        bx, by = self.p2
        cx, cy = self.p3
        d = (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) * 2
        x = ((ax**2 + ay**2)*(by - cy) +
             (bx**2 + by**2)*(cy - ay) +
             (cx**2 + cy**2)*(ay - by)) / d
        y = ((ay**2 + ax**2)*(cx - bx) +
             (by**2 + bx**2)*(ax - cx) +
             (cy**2 + cx**2)*(bx - ax)) / d
        r = math.sqrt((x - ax)**2 + (y - ay)**2)
        return ((x, y), r)


class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.__hash = None

    def __eq__(self, other):
        if (self.p1 == other.p1 and self.p2 == other.p2 or
                self.p2 == other.p1 and self.p1 == other.p2):
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if self.__hash is None:
            try:
                self.__hash = hash(self.p1) ^ hash(self.p2)
            except TypeError:
                print(self.p1, self.p2)
                raise
        return self.__hash


if __name__ == "__main__":
    import Image
    import ImageDraw
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimage
    import matplotlib.cm as cm
    import time
    plt.ion()
    plt.show()
    # full procedure
    gen_dun = generate_dungeon(21, 21, 3, 200)
    rooms = gen_dun.send(None)
    a = Image.new("RGBA", (100, 100), (255, 255, 255))
    draw = ImageDraw.Draw(a)
    for room in rooms:
        draw.rectangle(room.coords, outline=(0, 0, 0))
    plt.imshow(a, interpolation="nearest")
    plt.draw()
    time.sleep(1)
    terr = gen_dun.send(None)
    plt.imshow(terr, interpolation="nearest", cmap=cm.gray, origin="lower",
               vmin=0, vmax=1)
    plt.draw()
    time.sleep(5)
    terr2 = gen_dun.send(None)
    plt.imshow(terr2, interpolation="nearest", cmap=cm.gray, origin="lower")
    plt.draw()
    time.sleep(5)

from __future__ import division
import math
import random
import numpy as np

from render import render_terrain


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


def generate_dungeon(x, y, height, **options):
    """Generate a dungeon x by y cells, height cells high"""
    terrain = np.zeros([x, y], dtype=int)
    rooms = generate_rooms(x, y)
    yield rooms
    for room in rooms:
        carve(room, terrain)
    yield net_from_points([r.centre for r in rooms],
                          Triangle((0, 0), (0, x+y), (x+y, 0)))
    net = net_from_rooms(rooms, Triangle((0, 0), (0, x+y), (x+y, 0)))
    for l in net:
        if (l.p2.x1 < l.p1.x2) and (l.p2.x2 > l.p1.x1):
            corr_x = random.randint(max(l.p1.x1, l.p2.x1),
                                    min(l.p1.x2, l.p2.x2))
            carve(Room(corr_x, l.p1.centre[1], corr_x+1, l.p2.centre[1]),
                  terrain)
        elif (l.p2.y1 < l.p1.y2) and (l.p2.y2 > l.p1.y1):
            corr_y = random.randint(max(l.p1.y1, l.p2.y1),
                                    min(l.p1.y2, l.p2.y2))
            carve(Room(l.p1.centre[0], corr_y, l.p2.centre[0], corr_y+1),
                  terrain)
        else:
            corr_x = random.randint(l.p1.x1, l.p1.x2)
            corr_y = random.randint(l.p2.y1, l.p2.y2)
            carve(Room(corr_x, l.p1.centre[1], (corr_x + 1), corr_y+1),
                  terrain)
            carve(Room(corr_x, corr_y, l.p2.centre[0], (corr_y + 1)),
                  terrain)
    yield terrain
    # terr_temp = np.zeros([x+2, y+2], dtype=int)
    # terr_temp[1:-1, 1:-1] = terrain
    N_walls = np.logical_and(terrain == 0, np.roll(terrain, -1, 1) > 0)
    S_walls = np.logical_and(terrain == 0, np.roll(terrain, 1, 1) > 0)
    E_walls = np.logical_and(terrain == 0, np.roll(terrain, -1, 0) > 0)
    W_walls = np.logical_and(terrain == 0, np.roll(terrain, 1, 0) > 0)
    yield terrain + 2*N_walls + 4*S_walls + 8*E_walls + 16*W_walls


def generate_rooms(x, y):
    """Generate dungeon rooms x by y cells"""
    rooms = []
    for i in range(0, 20):
        added = False
        i = 0
        while added is False and i < 100:
            i += 1
            x1 = random.randint(1, x-1)
            x2 = random.randint(1, x-1)
            y1 = random.randint(1, y-1)
            y2 = random.randint(1, y-1)
            if abs(x1 - x2) < 4:
                continue
            if abs(y1 - y2) < 4:
                continue
            ratio = abs((x1-x2) / (y1-y2))
            if ratio < 0.2 or ratio > 5:
                continue
            room = Room(x1, y1, x2, y2)
            r = random.random()**4
            if room.area > r * x * y:
                continue
            if any(intersects(room, r) for r in rooms):
                continue
            else:
                rooms.append(room)
                added = True
    return rooms


def intersects(room1, room2):
    """Check whether the two rectangular rooms intersect"""
    x_int = ((room2.x1 < room1.x2 + 1) and (room2.x2 + 1 > room1.x1))
    y_int = ((room2.y1 < room1.y2 + 1) and (room2.y2 + 1 > room1.y1))
    if x_int and y_int:
        return True
    else:
        return False


def carve(room, terrain, n=1):
    for i in range(room.x1, room.x2):
        for j in range(room.y1, room.y2):
            terrain[i][j] = n


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


def net_from_points(points, outer_triangle):
    """Generates a net of connections from a list of points"""
    i_points = points[:]
    triangles = [outer_triangle]
    while i_points:
        point = i_points.pop(random.randint(0, len(i_points) - 1))
        rebuild_triangles = []
        for tri in triangles:
            if tri.in_circumcircle(point):
                rebuild_triangles.append(tri)
        polygon = set([])
        for i, tri in enumerate(rebuild_triangles):
            for line in tri:
                if sum([line in tri2 for tri2 in rebuild_triangles]) > 1:
                    continue
                polygon.add(line)
            triangles.remove(tri)
        for line in polygon:
            triangles.append(Triangle(line.p1, line.p2, point))
    net = set([])
    outer_points = [outer_triangle.p1, outer_triangle.p2, outer_triangle.p3]
    for tri in triangles:
        for l in tri:
            if l.p1 in outer_points or l.p2 in outer_points:
                continue
            net.add(l)
    return net


def net_from_rooms(rooms, outer_triangle):
    net = net_from_points([room.centre for room in rooms], outer_triangle)
    room_net = []
    for line in net:
        r1 = None
        r2 = None
        for r in rooms:
            if r.centre == line.p1:
                r1 = r
            if r.centre == line.p2:
                r2 = r
        if r1 is None or r2 is None:
            raise TypeError
        room_net.append(Line(r1, r2))
    return room_net


if __name__ == "__main__":
    import Image
    import ImageDraw
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import time
    plt.ion()
    plt.show()
    # full procedure
    gen_dun = generate_dungeon(40, 50, 3)
    rooms = gen_dun.send(None)
    net = gen_dun.send(None)
    a = Image.new("RGBA", (40, 50), (255, 255, 255))
    draw = ImageDraw.Draw(a)
    for room in rooms:
        draw.rectangle(room.coords, outline=(0, 0, 0))
    for line in net:
        draw.line((line.p1, line.p2), fill=(255, 0, 0))
    plt.imshow(a, interpolation="nearest")
    plt.draw()
    time.sleep(1)
    terr = gen_dun.send(None)
    plt.imshow(np.swapaxes(terr, 0, 1), interpolation="nearest", cmap=cm.gray,
               origin="upper")
    plt.draw()
    time.sleep(1)
    terr2 = gen_dun.send(None)
    plt.imshow(np.swapaxes(terr2, 0, 1), interpolation="nearest", cmap=cm.gray,
               origin="upper")
    plt.draw()
    time.sleep(1)
    im2 = render_terrain(terr2, "Dungeonset1")
    im2.show()

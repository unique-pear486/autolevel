from __future__ import division
import math
import random


class Room(object):
    """A room object. Occupys cells x1 to x2-1, y1 to y2-1"""
    def __init__(self, x1, y1, x2, y2):
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

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
    rooms = []
    for i in range(0, 20):
        added = False
        i = 0
        while added is False and i < 100:
            i += 1
            x1 = random.randint(0, x)
            x2 = random.randint(0, x)
            y1 = random.randint(0, y)
            y2 = random.randint(0, y)
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
    x_int = ((room2.x1 < room1.x2) and (room2.x2 > room1.x1))
    y_int = ((room2.y1 < room1.y2) and (room2.y2 > room1.y1))
    if x_int and y_int:
        return True
    else:
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


if __name__ == "__main__":
    import Image
    import ImageDraw
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimage
    import time
    plt.ion()
    plt.show()

    a = Image.new("RGBA", (100, 100), (255, 255, 255))
    draw = ImageDraw.Draw(a)
    rooms = generate_dungeon(100, 100, 3)
    for room in rooms:
        draw.rectangle(room.coords, outline=(0, 0, 0))
    plot = plt.imshow(a, interpolation="nearest")
    plt.draw()
    points = [room.centre for room in rooms]
    net = net_from_points(points, Triangle((0, 0), (600, 0), (0, 600)))
    for line in net:
        draw.line((line.p1, line.p2), fill=(255, 0, 0))
    plot = plt.imshow(a, interpolation="nearest")
    plt.draw()
    time.sleep(10)

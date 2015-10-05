from __future__ import division
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
        return [(self.x1 + self.x2)/2, (self.y1 + sefl.y2)/2]

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
    time.sleep(10)

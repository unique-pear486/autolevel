import Image
import json
import numpy as np
from random import randint


class tile_type(object):
    ground = 1
    N_wall = 2
    S_wall = 4
    E_wall = 8
    W_wall = 16

    @classmethod
    def __getitem__(cls, item):
        for i in cls.__dict__:
            if cls.__dict__[i] == item:
                return i
        raise KeyError(item)


def render_terrain(terrain, tile_set):
    """Render the terrain return a PIL Image"""
    with open("images/{}.json".format(tile_set)) as f:
        config = json.load(f)
    source = Image.open("images/" + config["file"])
    print(source.mode)
    size = (terrain.shape[0] * config["size"][0],
            terrain.shape[1] * config["size"][1])
    im = Image.new("RGBA", size)  # , color=(255, 0, 255))
    t = tile_type()
    for (i, j), tile in np.ndenumerate(terrain):
        try:
            tile = t[tile]
        except KeyError:
            continue
        try:
            loc = config[tile][randint(0, len(config[tile])-1)]
            tile = get_tile(source, config["size"], loc)
            box = (i * config["size"][0],
                   j * config["size"][1],
                   (i + 1) * config["size"][0],
                   (j + 1) * config["size"][1])
            im.paste(tile, box, tile)
        except KeyError:
            pass
    return im


def get_tile(source, size, location):
    box = (location[0] * size[0],
           location[1] * size[1],
           (location[0] + 1) * size[0],
           (location[1] + 1) * size[1],)
    return source.crop(box)


class Terrain(object):
    def __init__(self, x, y):
        self._tiles = []
        for i in range(x):
            self._tiles.append([])
            for j in range(y):
                self._tiles[-1].append(Tile(self, x=i, y=j, i=0))

    def __getitem__(self, pos):
        try:
            return self._tiles[pos[0]][pos[1]]
        except TypeError:
            return self._tiles[pos]
        else:
            raise TypeError("Index must be integer or 2-tuple")

    def __repr__(self):
        string = "["
        for i in self._tiles:
            string += "["
            string += ", ".join([str(j) for j in i])
            string += "]\n"
        string += "]"
        return string


class Tile(object):

    def __init__(self, terrain, x, y, i=0):
        self._terrain = terrain
        self.x = x
        self.y = y
        self.i = 0

    def __repr__(self):
        return "Tile(x={}, y={}, i={})".format(self.x,
                                               self.y,
                                               self.i)

    def __str__(self):
        return str(self.i)

    def n(self):
        if self.y == 0:
            return self
        return self._terrain[self.x][self.y - 1]

    def e(self):
        if self.x + 1 == len(self._terrain):
            return self
        return self._terrain[self.x + 1][self.y]

    def s(self):
        if self.y + 1 == len(self._terrain[0]):
            return self
        return self._terrain[self.x][self.y + 1]

    def w(self):
        if self.x == 0:
            return self
        return self._terrain[self.x - 1][self.y]


def render_minitile(terrain, tileset):
    pass


terr = Terrain(5, 5)
print(terr)
print(repr(terr[3, 4].n()))

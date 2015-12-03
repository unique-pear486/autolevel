import Image

import json
import numpy as np
from random import randint


# Tiles are numbered:
#   0  1
#   2  3
STANDARD_TILES = [[-1, -1, -1, -1], [0, 0, 0, 1], [0, 0, 1, 0],
                  [-1, -1, -1, -1], [0, 1, 0, 0], [1, 0, 0, 0],
                  [1, 1, 1, 0], [1, 1, 0, 0], [1, 1, 0, 1],
                  [1, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 1],
                  [1, 0, 1, 1], [0, 0, 1, 1], [0, 1, 1, 1]]


class tile_type(object):
    ground = 1
    N_wall = 2
    S_wall = 4
    E_wall = 8
    W_wall = 16

    def __getitem__(self, item):
        for i in self.__dict__:
            if self.__dict[i] == item:
                return i
        raise KeyError(item)


class Tile(object):
    def __init__(self, image, corners):
        self.image = image
        self.corners = corners

    def __getitem__(self, item):
        return self.corners[item]


class TileSet(object):
    def __init__(self, image, tilesize, tiles):
        self.image = Image.open(image)
        self.x = tilesize[0]
        self.y = tilesize[1]
        self.tiles = []
        column_max = self.image.size[0] // self.x
        row_max = self.image.size[1] // self.y
        print(row_max, column_max)
        for i in range(column_max):
            for j in range(row_max):
                print(i, j, i + column_max * j)
                self.tiles.append(Tile(
                    self.image.crop((i*self.x, j*self.y,
                                    (i+1)*self.x, (j+1)*self.y)),
                    tiles[i + column_max * j]
                    ))

    def __iter__(self):
        return iter(self.tiles)


def render_terrain(terrain, tile_set):
    """Render the terrain return a PIL Image"""
    with open("images/{}.json".format(tile_set)) as f:
        config = json.load(f)
    source = Image.open("images/{}.png".format(tile_set))
    size = (terrain.shape[0] * config["size"][0],
            terrain.shape[1] * config["size"][1])
    im = Image.new("RGB", size, color=(255, 0, 255))
    for (i, j), tile in np.ndenumerate(terrain):
        if tile == 1:
            loc = config["ground"][randint(0, len(config["ground"])-1)]
            print(loc)
            tile = get_tile(source, config["size"], loc)
            box = (i * config["size"][0],
                   j * config["size"][1],
                   (i + 1) * config["size"][0],
                   (j + 1) * config["size"][1])
            im.paste(tile, box)
    return im


def get_tile(source, size, location):
    box = (location[0] * size[0],
           location[1] * size[1],
           (location[0] + 1) * size[0],
           (location[1] + 1) * size[1],)
    return source.crop(box)


def render_dynamic_tile(tile, tile_set):
    corners = ["NW", "NE", "SE", "SW"]
    x = tile_set.x
    y = tile_set.y
    im = Image.new("RGB", (x, y), color=(255, 0, 255))
    NW, NE, SW, SE = None, None, None, None
    for corner in corners:
        if corner == "NW":
            N = tile.North.val
            W = tile.West.val
            This = tile.val
            for t in tile_set:
                if t[3] == This and t[1] == N and t[2] == W:
                    NW = t
        if corner == "NE":
            N = tile.North.val
            E = tile.East.val
            This = tile.val
            for t in tile_set:
                if t[2] == This and t[0] == N and t[3] == E:
                    NE = t
        if corner == "SE":
            S = tile.South.val
            E = tile.East.val
            This = tile.val
            for t in tile_set:
                if t[0] == This and t[3] == S and t[1] == E:
                    SE = t
        if corner == "SW":
            S = tile.South.val
            W = tile.West.val
            This = tile.val
            print("SW", W, This, "x", S)
            for t in tile_set:
                if t[1] == This and t[3] == S and t[0] == W:
                    SW = t
    if None in [NW, NE, SW, SE]:
        raise KeyError("Tile not found", [NW, NE, SW, SE])
    im.paste(NW.image.crop((x // 2, y // 2, x, y)), (0, 0))
    im.paste(NE.image.crop((0, y // 2, x // 2, y)), (x // 2, 0))
    im.paste(SW.image.crop((x // 2, 0, x, y // 2)), (0, y // 2))
    im.paste(SE.image.crop((0, 0, x // 2, y // 2)), (x // 2, y // 2))
    im.show()


ground = TileSet("images/base.png", [32, 32], STANDARD_TILES)
for t in ground:
    print(t[0], t[1], t[2], t[3])

def a():
    pass


def b():
    pass
a.val = 1
b.val = 0
a.North = b
a.South = b
a.West = b
a.East = b

render_dynamic_tile(a, ground)

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

    def __getitem__(self, item):
        for i in self.__dict__:
            if self.__dict[i] == item:
                return i
        raise KeyError(item)


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

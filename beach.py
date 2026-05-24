"""
-*- coding: utf-8 -*-
@Time    : 2026-05-16
@Github  : windbell0711/Vatrix-vbe-sm
@File    : beach.py
@Author  : windbell0711
"""
import engine
from consts import *

def test(g):
    g.spawn_plant(col=0, row=2, typ=pt.min).special_cd = 2
    g.spawn_plant(col=1, row=2, typ=pt.nut).hp = 800
    g.spawn_zombie(row=2, typ=zt.bkt, pos_x=180, v=None)
    g.spawn_zombie(row=2, typ=zt.bkt, pos_x=180, v=None)

    # vs = [
    #     g.spawn_vase(row=2, col=1, content=zt.bkt, vase_type='zombie'),
    #     g.spawn_vase(row=2, col=2, content=zt.jac, vase_type='zombie'),
    #     g.spawn_vase(row=2, col=3, content=zt.zom, vase_type='zombie'),
    #     g.spawn_vase(row=1, col=2, content=zt.zom, vase_type='zombie'),
    # ]
    # g.open_vase(vs[1])

    # g.spawn_plant (pt.rep, row=2, col=2)
    # g.spawn_plant (pt.squ, row=2, col=1)
    # g.spawn_plant (pt.nut, row=2, col=2)
    # g.spawn_zombie(zt.ggt, row=2, col=4, v=engine.math.inf)
    # g.spawn_zombie(zt.bkt, row=2, col=3, v=-engine.math.inf)


def multi_test(loops: int = 500):
    win, tot = 0, 0
    for _ in range(loops):
        g = engine.VbGame()
        test(g)
        # cnt = 0
        while not (g.win or g.lose):
            g.update_game()
            # cnt += 1
            # if cnt % 10 == 0:
            #     if input():
            #         print(g)
        win += g.win
        tot += 1
    print(f"{win=} / {tot=} = {100*win/tot}%")


if __name__ == '__main__':
    multi_test()

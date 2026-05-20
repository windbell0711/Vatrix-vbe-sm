"""
-*- coding: utf-8 -*-
@Time    : 2026-05-16
@Github  : windbell0711/Vatrix-vbe-sm
@File    : beach.py
@Author  : windbell0711
"""
import engine
from consts import *

g = engine.VbGame()

def test():
    # p = g.spawn_plant(col=0, row=2, typ=pt.min)
    # p.special_cd = 2
    # g.spawn_plant(col=7, row=2, typ=pt.rre)
    # g.spawn_plant(col=1, row=2, typ=pt.nut)
    # g.spawn_plant(col=7, row=1, typ=pt.che)
    # g.open_vase(g.spawn_vase(col=2, row=2, content=zt.bkt, vase_type='zombie'))
    # g.open_vase(g.spawn_vase(col=6, row=1, content=zt.con, vase_type='zombie'))
    # g.spawn_zombie(row=2, typ=zt.bkt, pos_x=150, v=None)
    # g.spawn_zombie(row=2, typ=zt.bkt, pos_x=150, v=None)
    g.spawn_plant(row=2, col=0, typ=pt.squ)
    z1 = g.spawn_zombie(row=2, typ=zt.bkt, pos_x=139.9)
    z2 = g.spawn_zombie(row=2, typ=zt.bkt, pos_x=184.8)
    z1.v = z2.v = 0


if __name__ == '__main__':
    win, tot = 0, 0
    for _ in range(2000):
        g = engine.VbGame()
        test()
        cnt = 0
        while not (g.win or g.lose):
            g.update_game()
            # cnt += 1
            # if cnt % 10 == 0:
            #     if input():
            #         print(g)
        win += g.win
        tot += 1
    print(f"{win=} / {tot=} = {100*win/tot}%")

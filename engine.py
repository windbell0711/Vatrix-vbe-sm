"""
-*- coding: utf-8 -*-
@Time    : 2026-05-16
@Github  : windbell0711/Vatrix-vbe-sm
@File    : engine.py
@Author  : windbell0711
"""
from typing import Literal, Optional
from utils import *


class VbGame:
    def __init__(self):
        self.tick: int = 0
        self.sun: int = 0

        self.zombies: list[Zombie] = []
        self.plants: list[Plant] = []
        self.vases: list[Vase] = []
        self.seeds: list[Seed] = []

        self.win: bool = False
        self.lose: bool = False

    def __str__(self) -> str:
        return (f"Game(\ntick={self.tick}, sun={self.sun},{' WIN' if self.win else ''}{' LOSE' if self.lose else ''}\n"
                f"zombies=[{',\n         '.join(map(str, self.zombies))}],\nplants= [{',\n         '.join(map(str, self.plants))}]\nvases=  [{',\n         '.join(map(str, self.vases))}]\n)")

    def spawn_plant(self, typ: int, row: int, col: int) -> Plant:
        """生成植物"""
        x, y = grid_to_pixel(col, row)
        plant = Plant(
            typ=typ,
            row=row,
            col=col,
            x=x,
            y=y,
        )
        self.plants.append(plant)
        return plant

    def spawn_zombie(self, typ: int, row: int, col: Optional[int] = None, pos_x: Optional[float] = None, v: Optional[float] = None, **kwargs) -> Zombie:
        """生成僵尸"""
        if kwargs:
            print(f"spawn_zombie got extra args: {kwargs}")
        if pos_x is not None:
            assert col is None
            x = pos_x
        elif col is not None:
            assert pos_x is None
            x = grid_to_pixel(col, row)[0]
        else:
            x = {zt.ggt: 845 + random.randint(0, 10),
                 zt.pol: 870 + random.randint(0, 10),
                 zt.zbn: 800 + random.randint(0, 10),
                 zt.ctp: 825 + random.randint(0, 10),
                 zt.flg: 800 } \
               .get(typ, 780 + random.randint(0, 40))
        zombie = Zombie(
            typ=typ,
            row=row,
            x=x,
            y=grid_to_pixel(0, row)[1],
            v=v,
            **kwargs
        )
        self.zombies.append(zombie)
        return zombie

    def kill_plants_in_radius(self, x: float, y: float, r: float) -> None:
        """在指定半径内击杀植物"""
        for p in self.plants:
            if GetCircleRectOverlap(x, y, r, p.rect):
                p.hp = 0

    def kill_zombies_in_radius(self, x: float, y: float, r: float, row: int, row_extend: int, damage: Optional[int] = None) -> None:
        """在指定半径内击杀植物"""
        for z in self.zombies:
            if abs(z.row - row) <= row_extend and GetCircleRectOverlap(x, y, r, z.rect):
                if damage is None:
                    z.hp = 0
                else:
                    z.deal_damage(damage)


    def spawn_vase(self, content: int, row: int, col: int, vase_type: Optional[Literal['seed', 'zombie', 'sun']] = None) -> Vase:
        """生成罐子"""
        if vase_type is None:
            if content == -1:
                vase_type = 'sun'
            elif pt.left <= content <= pt.right:
                vase_type = 'seed'
            elif zt.left <= content <= zt.right:
                vase_type = 'zombie'
            else:
                raise ValueError(f"Unknown content type: {content}")
        self.vases.append(vase := Vase(
            row=row,
            col=col,
            vase_type=vase_type,
            content=content
        ))
        return vase

    def open_vase(self, vase: Vase) -> Seed | Zombie | None:
        match vase.vase_type:
            case 'seed':
                ret = self.spawn_seed(vase.content)
            case 'zombie':
                ret = self.spawn_zombie(vase.content, vase.row, pos_x=grid_to_pixel(vase.col, vase.row)[0])
            case 'sun':
                self.sun += 50
                ret = None
            case 'plant':
                # 如果将来需要支持直接种植物，应该这样调用：
                # self.spawn_plant(typ=vase.content, row=vase.row, col=vase.col)
                raise NotImplementedError(f"vase_type of {vase} '{vase.vase_type}' not implemented, do u mean 'seed'?")
            case _:
                raise NotImplementedError(f"Unknown vase type: {vase.vase_type}")
        vase.exist = False
        return ret

    def open_vase_in_square(self, col: int, row: int, extend: int = 1) -> None:
        """打开指定范围内的罐子"""
        for v in self.vases:
            if abs(v.col - col) <= extend and abs(v.row - row) <= extend:
                self.open_vase(v)

    def find_vase(self, col: int, row: int) -> Optional[Vase]:
        for v in self.vases:
            if v.col == col and v.row == row:
                return v
        return None

    def spawn_seed(self, typ: int) -> Seed:
        self.seeds.append(seed := Seed(typ=typ, fade_cd=300))
        return seed

    def check_win(self) -> None:
        if not self.win and len(self.zombies) == 0 and len(self.vases) == 0:
            self.win = True


    def update_game(self):
        """执行一个 tick 的游戏逻辑"""
        self.tick += 1

        # 1. 植物攻击
        self.update_plants()

        # 2. 僵尸移动 & 啃食
        self.update_zombies()

        # 3. 清理死亡植物/僵尸
        self.plants  = [p for p in self.plants  if p.hp > 0]
        self.zombies = [z for z in self.zombies if z.hp > 0]
        self.vases   = [v for v in self.vases   if v.exist]
        self.seeds   = [s for s in self.seeds   if s.fade_cd > 0]

        # 4. 胜利检查
        if not self.win and not self.lose:
            self.check_win()


    def update_plants(self):
        for pla in self.plants:
            # 0. 自减cd
            if pla.special_cd > 0:    pla.special_cd -= 1
            if pla.launch_rate != -1: pla.launch_cd  -= 1
            # 1. 发射逻辑
            if pla.launch_rate != -1 and pla.launch_cd <= 0:
                pla.launch_cd = pla.launch_rate  # 初始化发射倒计时
                # 找同行、在攻击范围内、最近（x 最小）的僵尸
                attackable = [z for z in self.zombies if
                              z.row == pla.row and GetRectOverlap(pla.attack_rect, z.rect) > 0]
                # 实施伤害 & 效果
                if attackable:
                    find_maxinimum = max if pla.typ == pt.rre else min
                    target = find_maxinimum(attackable, key=lambda z: z.x)
                    target.deal_damage(pla.launch_damage)
                    if pla.typ == pt.sno:
                        target.chilled_cd = 200
                # 特判
                if pla.typ == pt.thr:  # 三线射手另外两个子弹
                    for dy in (-1, 1):
                        attackable = [z for z in self.zombies if
                                      z.row == pla.row + dy and GetRectOverlap(
                                          pla.attack_rect.get_moved(0, dy * CELL_H), z.rect) > 0]
                        if attackable:
                            target = min(attackable, key=lambda z: z.x)
                            target.deal_damage(pla.launch_damage)
            # 2. 樱桃更新
            elif pla.typ == pt.che and pla.special_cd <= 0:
                self.kill_zombies_in_radius(pla.x, pla.y, r=115, row=pla.row, row_extend=1, damage=1800)
                pla.hp = 0
            # 3. 土豆更新
            elif pla.typ == pt.min:
                if pla.state == 'not_ready':
                    if pla.special_cd <= 0:
                        pla.state = 'rising'
                        pla.hp = A_REALLY_BIG_NUMBER
                        pla.special_cd = 106
                elif pla.state == 'rising':
                    if pla.special_cd <= 0:
                        pla.state = 'armed'
                elif pla.state == 'armed':
                    attackable = [z for z in self.zombies if
                                  z.row == pla.row and GetRectOverlap(pla.attack_rect, z.rect) >=
                                  (-30 if z.is_eating else 0)]
                    if attackable:
                        self.kill_zombies_in_radius(pla.x + 20, pla.y + 40,  # aPosX = mX + mWidth / 2 - 20; aPosY = mY + mHeight / 2;
                                                    r=60, row=pla.row, row_extend=1, damage=1800)  # mBoard->KillAllZombiesInRadius(mRow, aPosX, aPosY, 60, 0, false, aDamageRangeFlags)
                        pla.hp = 0
                else:
                    raise ValueError(f"Unknown plant state: {pla}")
            # 5. 窝瓜更新
            elif pla.typ == pt.squ:
                def find_squ_tar() -> Optional[Zombie]:
                    closest_zom: Optional[Zombie] = None
                    for z in self.zombies:
                        if (z.row == pla.row and
                            (GetRectOverlap(pla.attack_rect, closest_zom.rect) if closest_zom else math.inf) > GetRectOverlap(pla.attack_rect, z.rect) >= (-110 if z.is_eating else -70) and
                            z.rect.x + z.rect.w >= pla.attack_rect.x - 60):
                                closest_zom = z
                    return closest_zom
                if pla.state == 'not_ready':
                    if find_squ_tar():
                        # plant.target_x 不必在此处计算
                        pla.state = "squash_pre_launch"
                        pla.special_cd = 125
                elif pla.state == 'squash_pre_launch':
                    if pla.special_cd <= 0:
                        if zombie := find_squ_tar():
                            pla.x = (zombie.rect.x + zombie.rect.w / 2
                                - 30 * zombie.v * (0.5 if zombie.chilled_cd > 0 else 1) * (not zombie.is_eating)) - 40
                            pla.y -= 112
                            pla.state = "squash_rise_and_fall"
                            pla.special_cd = 60
                elif pla.state == 'squash_rise_and_fall':
                    if pla.special_cd == 5:
                        pla.y += 60
                        pla.attack_rect = Rect(pla.x + 20, pla.y, 80 - 35, 80)
                        for z in self.zombies:
                            if z.row == pla.row and GetRectOverlap(pla.attack_rect, z.rect) > 0:
                                z.deal_damage(1800)
                    if pla.special_cd <= 0:
                        pla.hp = 0
                else:
                    raise ValueError(f"Unknown plant state: {pla}")


    def update_zombies(self):
        for zom in self.zombies:
            if zom.special_cd > 0:  zom.special_cd -= 1
            if zom.chilled_cd > 0:  zom.chilled_cd -= 1

            def find_target_plant() -> Optional[Plant]:
                """找到僵尸的目标植物（啃砸范围内）"""
                for p in self.plants:
                    if p.row == zom.row:
                        if GetRectOverlap(zom.attack_rect, p.rect) >= 20:
                            return p
                return None

            # 1. 啃食
            if zom.typ != zt.ggt:
                target_p = find_target_plant()
                if target_p:
                    zom.is_eating = True
                    target_p.hp -= 1  # 简化啃食机制
                else:
                    zom.is_eating = False
            # 2. 移动
            zom.move_a_tick()
            zom.update_rects()
            # 3. 判定僵尸进家
            if (zom.x < -100 and zom.typ not in (zt.ftb, zt.zbn, zt.ctp, zt.pol, zt.ggt, zt.dan, zt.dab, zt.snk)) or \
               (zom.x < -175 and zom.typ in (zt.ftb, zt.zbn, zt.ctp)) or \
               (zom.x < -150 and zom.typ in (zt.pol, zt.ggt)) or \
               (zom.x < -130 and zom.typ in (zt.dan, zt.dab, zt.snk)):
                self.lose = True
            # 4. 特判小丑
            if zom.typ == zt.jac:
                if zom.phase == 'running':
                    if zom.special_cd <= 0:
                        zom.v = 0
                        zom.hp = A_REALLY_BIG_NUMBER  # 视作无敌，忽略樱桃炸丑的可能
                        zom.special_cd = 110
                        zom.phase = 'popping'
                elif zom.phase == 'popping':
                    if zom.special_cd <= 0:
                        self.kill_plants_in_radius(zom.x + 60, zom.y + 60, r=90)
                        self.open_vase_in_square(*pixel_to_grid(zom.x + 60, zom.y + 60))
                        zom.hp = 0
                else:
                    raise ValueError(f"Unknown zombie phase: {zom}")
            # 5. 特判巨人
            elif zom.typ == zt.ggt:
                if zom.phase == 'normal':
                    if (p := find_target_plant()) and p.state != "squash_rise_and_fall" \
                            or self.find_vase(*pixel_to_grid(zom.x, zom.y)):
                        zom.special_cd = 207  # 开始锤击到命中1.34秒，命中到收手0.73秒。
                        zom.phase = 'smashing'
                    elif zom.has_object and zom.x > 400 and zom.hp < 3000 / 2:
                        zom.special_cd = 105  # 开始扔小鬼到小鬼出生1.05秒，小鬼出生到巨人收手0.37秒。
                        zom.has_object = False
                        zom.phase = 'throwing'
                elif zom.phase == 'smashing':
                    if zom.special_cd == 73:
                        if target_p := find_target_plant():
                            for p in self.plants:
                                if p.row == target_p.row and p.col == target_p.col:
                                    if p.typ == pt.min:  # 特判地雷在被砸的时候爆炸
                                        self.kill_zombies_in_radius(p.x + 20, p.y + 40, r=60, row=p.row, row_extend=1, damage=1800)
                                    if p.typ == pt.che:  # 特判樱桃在被砸的时候爆炸
                                        self.kill_zombies_in_radius(p.x, p.y, r=115, row=p.row, row_extend=1, damage=1800)
                                    if p.typ != pt.squ:  # 想了想，好像永远砸不掉窝瓜
                                        p.hp = 0
                        if target_v := self.find_vase(*pixel_to_grid(zom.x, zom.y)):
                            self.open_vase(target_v)
                    elif zom.special_cd <= 0:
                        zom.phase = 'normal'
                elif zom.phase == 'throwing':
                    # 扔出小鬼视为游戏结束，因为我怎么想都觉得这是下下策
                    if zom.special_cd <= 0:
                        zom.phase = 'normal'
                        self.lose = True
                else:
                    raise ValueError(f"Unknown zombie phase: {zom}")


if __name__ == '__main__':
    g = VbGame()
    g.spawn_plant(col=8, row=2, typ=pt.rre)
    g.spawn_plant(col=0, row=2, typ=pt.pea)
    v = g.spawn_vase(col=7, row=2, content=zt.bkt, vase_type='zombie')
    # p = g.spawn_plant(col=3, row=2, typ=pt.nut)
    # v = g.spawn_vase(col=3, row=2, content=zt.bkt, vase_type='zombie')
    z = g.open_vase(v)
    print(g)
    for _ in range(9999):
        g.update_game()
        # if p.hp < 4:
        #     print(_)
        #     break
        if g.lose or g.win:
            break
    print(g)

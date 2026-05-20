"""
-*- coding: utf-8 -*-
@Time    : 2026-05-16
@Github  : windbell0711/Vatrix-vbe-sm
@File    : engine.py
@Author  : windbell0711
"""
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
        return f"Game(\ntick={self.tick}, sun={self.sun},{' WIN' if self.win else ''}{' LOSE' if self.lose else ''}\nzombies=[{',\n         '.join(map(str, self.zombies))}],\nplants= [{',\n         '.join(map(str, self.plants))}]\n)"

    def spawn_plant(self, col: int, row: int, typ: int) -> Plant:
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

    def spawn_zombie(self, row: int, typ: int, pos_x: Optional[float] = None, v: Optional[float] = None) -> Zombie:
        """生成僵尸"""
        x = pos_x or 780 + random.randint(0, 40)
        _, y = grid_to_pixel(0, row)
        zombie = Zombie(
            typ=typ,
            row=row,
            x=x,
            y=y,
            v=v,
        )
        self.zombies.append(zombie)
        return zombie

    def kill_in_radius(self, obj: Iterable[Plant | Zombie], x: float, y: float, r: float, row: int,
                       row_extend: int) -> None:
        """在指定半径内击杀植物或僵尸"""
        for o in obj:
            if abs(o.row - row) <= row_extend and GetCircleRectOverlap(x, y, r, o.rect):
                if isinstance(o, Plant | Zombie):
                    o.hp = 0
                else:
                    raise ValueError(f"Unknown object type: {o}")


    def spawn_vase(self, col: int, row: int, content: int, vase_type) -> Vase:
        """生成罐子"""
        self.vases.append(vase := Vase(
            col=col,
            row=row,
            vase_type=vase_type,
            content=content
        ))
        return vase

    def open_vase(self, vase: Vase) -> Seed | Zombie | None:
        match vase.vase_type:
            case 'seed':
                ret = self.spawn_seed(vase.content)
            case 'zombie':
                ret = self.spawn_zombie(vase.row, vase.content, pos_x=grid_to_pixel(vase.col, vase.row)[0])
            case 'sun':
                self.sun += vase.content
            case 'plant':
                raise NotImplementedError(f"vase_type of {vase} '{vase.vase_type}' not implemented, do u mean 'seed'?")
                self.spawn_plant(vase.col, vase.row, vase.content)
            case _:
                raise NotImplementedError(f"Unknown vase type: {vase.vase_type}")
        self.vases.remove(vase)
        return ret

    def open_vase_in_square(self, col: int, row: int, extend: int = 1) -> None:
        """打开指定范围内的罐子"""
        for v in self.vases:
            if abs(v.col - col) <= extend and abs(v.row - row) <= extend:
                self.open_vase(v)


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
        self.plants =  [p for p in self.plants  if p.hp > 0]
        self.zombies = [z for z in self.zombies if z.hp > 0]

        # 4. 胜利检查
        self.check_win()


    def update_plants(self):
        for plant in self.plants:
            # 0. 自减cd
            if plant.special_cd > 0:    plant.special_cd -= 1
            if plant.launch_rate != -1: plant.launch_cd  -= 1
            # 1. 发射逻辑
            if plant.launch_rate != -1 and plant.launch_cd <= 0:
                plant.launch_cd = plant.launch_rate  # 初始化发射倒计时
                # 找同行、在攻击范围内、最近（x 最小）的僵尸
                attackable = [z for z in self.zombies if
                              z.row == plant.row and GetRectOverlap(plant.attack_rect, z.rect) > 0]
                # 实施伤害 & 效果
                if attackable:
                    find_maxinimum = max if plant.typ == pt.rre else min
                    target = find_maxinimum(attackable, key=lambda z: z.x)
                    target.deal_damage(plant.launch_damage)
                    if plant.typ == pt.sno:
                        target.chilled_cd = 200
                # 特判
                if plant.typ == pt.thr:  # 三线射手另外两个子弹
                    for dy in (-1, 1):
                        attackable = [z for z in self.zombies if
                                      z.row == plant.row + dy and GetRectOverlap(
                                          plant.attack_rect.get_moved(0, dy * CELL_H), z.rect) > 0]
                        if attackable:
                            target = min(attackable, key=lambda z: z.x)
                            target.deal_damage(plant.launch_damage)
            # 2. 樱桃更新
            elif plant.typ == pt.che and plant.special_cd <= 0:
                self.kill_in_radius(self.zombies, plant.x, plant.y, r=115, row=plant.row, row_extend=1)
                plant.hp = 0
            # 3. 土豆更新
            elif plant.typ == pt.min:
                if plant.state == 'not_ready':
                    if plant.special_cd <= 0:
                        plant.state = 'rising'
                        plant.hp = A_REALLY_BIG_NUMBER
                        plant.special_cd = 106
                elif plant.state == 'rising':
                    if plant.special_cd <= 0:
                        plant.state = 'armed'
                elif plant.state == 'armed':
                    attackable = [z for z in self.zombies if
                                  z.row == plant.row and GetRectOverlap(plant.attack_rect, z.rect) >=
                                  (-30 if z.is_eating else 0)]
                    if attackable:
                        self.kill_in_radius(self.zombies, plant.x + 20, plant.y + 40,  # aPosX = mX + mWidth / 2 - 20; aPosY = mY + mHeight / 2;
                                            r=60, row=plant.row, row_extend=1)  # mBoard->KillAllZombiesInRadius(mRow, aPosX, aPosY, 60, 0, false, aDamageRangeFlags)
                        plant.hp = 0
                else:
                    raise ValueError(f"Unknown plant state: {plant}")
            # 5. 倭瓜更新
            elif plant.typ == pt.squ:
                def find_squ_tar() -> Optional[Zombie]:
                    closest_zom: Optional[Zombie] = None
                    for z in self.zombies:
                        if (z.row == plant.row and
                            (GetRectOverlap(plant.attack_rect, closest_zom.rect) if closest_zom else math.inf) > GetRectOverlap(plant.attack_rect, z.rect) >= (-110 if z.is_eating else -70) and
                            z.rect.x + z.rect.w >= plant.attack_rect.x - 60):
                                closest_zom = z
                    return closest_zom
                if plant.state == 'not_ready':
                    if find_squ_tar():
                        # plant.target_x 不必此处计算
                        plant.state = "squash_pre_launch"
                        plant.special_cd = 110
                elif plant.state == 'squash_pre_launch':
                    if plant.special_cd <= 0:
                        if zom := find_squ_tar():
                            plant.x = (zom.rect.x + zom.rect.w / 2
                                - 30 * zom.v * (0.5 if zom.chilled_cd > 0 else 1) * (not zom.is_eating)) - 40
                            plant.y -= 112
                            plant.state = "squash_rise_and_fall"
                            plant.special_cd = 60
                elif plant.state == 'squash_rise_and_fall':
                    if plant.special_cd == 5:
                        plant.y += 60
                        plant.attack_rect = Rect(plant.x + 20, plant.y, 80 - 35, 80)
                        for z in self.zombies:
                            if z.row == plant.row and GetRectOverlap(plant.attack_rect, z.rect) > 0:
                                z.deal_damage(1800)
                    if plant.special_cd <= 0:
                        plant.hp = 0
                else:
                    raise ValueError(f"Unknown plant state: {plant}")


    def update_zombies(self):
        for zombie in self.zombies:
            if zombie.chilled_cd > 0:
                zombie.chilled_cd -= 1

            # 找到僵尸的目标植物（同行、在啃食范围内）
            target = None
            for p in self.plants:
                if p.row == zombie.row:
                    if GetRectOverlap(zombie.attack_rect, p.rect) >= 20:
                        target = p
                        break
            if target:
                zombie.is_eating = True
                target.hp -= 1  # 简化啃食机制
            else:
                zombie.is_eating = False
                speed = zombie.v
                if zombie.chilled_cd > 0:
                    speed *= 0.5
                zombie.x -= speed
                update_zombie_rects(zombie)

            if (zombie.x < -100) or \
                    (zombie.x < -175 and zombie.typ in (zt.ftb, zt.zbn, zt.ctp)) or \
                    (zombie.x < -150 and zombie.typ in (zt.pol, zt.ggt)) or \
                    (zombie.x < -130 and zombie.typ in (zt.dan, zt.dab, zt.snk)):
                self.lose = True


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

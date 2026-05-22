"""
-*- coding: utf-8 -*-
@Time    : 2026-05-16
@Github  : windbell0711/Vatrix-vbe-sm
@File    : utils.py
@Author  : windbell0711
"""
import math
from dataclasses import dataclass, field
from typing import Literal, Optional, Iterable
import random

from consts import pt, zt


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.w, self.h)

    def get_centre(self) -> tuple[float, float]:
        return (self.x + self.w / 2, self.y + self.h / 2)

    def get_moved(self, dx: float, dy: float):
        return Rect(self.x + dx, self.y + dy, self.w, self.h)

    def __repr__(self) -> str:
        return f"Rect{[int(a) for a in (self.x, self.y, self.w, self.h)]}"


# 僵尸
# hp 默认270-70
ZOMBIE_BODY_HP = {zt.jac: 500 - 166, zt.ggt: 3000}
# helm_hp 默认0
ZOMBIE_HELM_HP = {zt.con: 370, zt.bkt: 1100}
# vel   # RandRangeFloat(0.23f, 0.32f)
ZOMBIE_VEL_MIN = {zt.jac: 0.66}
ZOMBIE_VEL_MAX = {zt.jac: 0.68}
# special_cd 默认0
ZOMBIE_SPECIAL_CD = {zt.jac: 10}
# phase 默认none
ZOMBIE_PHASE = {zt.jac: 'running', zt.ggt: 'normal'}
# rects
ZOMBIE_RECT = {z: Rect(36, 0, 42, 115) for z in (zt.zom, zt.con, zt.bkt)} | \
              {zt.ggt: Rect(-17, -38, 125, 154),
               zt.jac: Rect(36, 0, 42, 115)}
ZOMBIE_ATT_RECT = {z: Rect(20, 0, 50, 115) for z in (zt.zom, zt.con, zt.bkt)} | \
                  {zt.ggt: Rect(-30, -38, 89, 154),
                   zt.jac: Rect(20, 0, 50, 115)}

@dataclass
class Zombie:
    typ    : int
    row    : int
    x      : float
    y      : float
    hp     : int = field(init=False)
    helm_hp: int = field(init=False)
    v      : Optional[float] = None  # inf, -inf 可以控制大小; None 取随机值; nan 取平均值
    rect       : Rect = field(init=False)
    attack_rect: Rect = field(init=False)
    special_cd : int  = field(init=False)
    phase      : str  = field(init=False)
    has_object : bool = True
    chilled_cd : int  = 0
    is_eating  : bool = False

    def initiate_zombie(self) -> None:
        # 1. hp
        self.hp = ZOMBIE_BODY_HP.get(self.typ, 270 - 70)
        # 2. helm_hp
        self.helm_hp = ZOMBIE_HELM_HP.get(self.typ, 0)
        # 3. vel
        self.v: float
        a = ZOMBIE_VEL_MIN.get(self.typ, 0.47 * 0.23)
        b = ZOMBIE_VEL_MAX.get(self.typ, 0.47 * 0.37)
        if self.v is None:
            self.v = random.uniform(a, b)
        elif self.v == math.inf:
            self.v = a
        elif self.v == -math.inf:
            self.v = b
        elif self.v == math.nan:
            self.v = (a + b) / 2
        else:
            if not self.v or not a <= self.v <= b:
                raise ValueError(f"{self.typ=} vel={self.v} not in {a=}, {b=}")
            self.v = float(self.v)
        # 4. rects
        self.update_rects()
        # 5. phase
        self.special_cd = ZOMBIE_SPECIAL_CD.get(self.typ, 0)
        self.phase = ZOMBIE_PHASE.get(self.typ, 'none')

    def update_rects(self):
        self.rect        = ZOMBIE_RECT    [self.typ].get_moved(self.x, self.y)
        self.attack_rect = ZOMBIE_ATT_RECT[self.typ].get_moved(self.x, self.y)

    def __post_init__(self) -> None:
        self.initiate_zombie()

    def deal_damage(self, damage: int) -> None:
        """对僵尸造成伤害"""
        if self.helm_hp > 0:
            taken = min(damage, self.helm_hp)
            self.helm_hp -= taken
            damage -= taken
        if damage > 0:
            self.hp -= damage


# 植物
# hp 默认300
PLANT_HP = {pt.nut: 4000}
# 攻击间隔 默认不攻击
PLANT_RATE = ({p: 150 - 6 for p in (pt.pea, pt.sno, pt.rep, pt.rre, pt.thr)} |
              {})
# 攻击伤害 默认0
PLANT_DAMAGE = ({p: 20 for p in (pt.pea, pt.sno, pt.thr)} |
                {p: 40 for p in (pt.rep, pt.rre)})
# 特殊攻击冷却 默认0
PLANT_SPECIAL_CD = ({pt.che: 100, pt.min: 1500})
# 当前状态 默认none
PLANT_STATE = {pt.min: 'not_ready', pt.squ: 'not_ready'}

@dataclass
class Plant:
    typ: int
    row: int
    col: int
    x: float
    y: float
    hp: int            = field(init=False)
    launch_cd: int     = field(init=False)
    launch_rate: int   = field(init=False)
    launch_damage: int = field(init=False)
    special_cd: int    = field(init=False)
    state: str         = field(init=False)
    target_zom: Optional[Zombie] = field(init=False)
    rect: Rect         = field(init=False)
    attack_rect: Rect  = field(init=False)

    def initiate_plant(self) -> None:
        # 1. hp
        self.hp = PLANT_HP.get(self.typ, 300)
        # 2. launch_rate
        self.launch_rate = self.launch_cd = PLANT_RATE.get(self.typ, -1)
        # 3. launch_damage
        self.launch_damage = PLANT_DAMAGE.get(self.typ, 0)
        # 4. special_cd
        self.special_cd = PLANT_SPECIAL_CD.get(self.typ, 0)
        # 5. state
        self.state = PLANT_STATE.get(self.typ, 'none')
        self.target_zom = None
        # 6. rect
        x, y = self.x, self.y
        self.rect = Rect(x + 10, y, 60, 80)
        # 7. attack_rect
        width = 80 if self.typ != pt.pum else 120
        height = 80
        match self.typ:
            case pt.rre:
                re = Rect(0, y, x, height)
            case pt.squ:  # SQUASH
                re = Rect(x + 20, y, width - 35, height)
            case pt.min:  # POTATOMINE
                re = Rect(x, y, width - 25, height)
            case pt.pea | pt.sno | pt.thr:
                re = Rect(x + 60, y, BOARD_WIDTH, height)
            case _:
                re = Rect(x + 60, y, BOARD_WIDTH, height)
        self.attack_rect = re

    def __post_init__(self) -> None:
        self.initiate_plant()


@dataclass
class Seed:
    typ: int
    fade_cd: int


@dataclass
class GridItem:
    row: int
    col: int

@dataclass
class Vase(GridItem):
    vase_type: Literal['seed'] | Literal['zombie'] | Literal['sun']
    content: int  # pt.* or zt.* or -1
    transparent: bool = False
    exist: bool = True


# ============================================================================
# 常量表
# ============================================================================

# 坐标系（普通草坪）
CELL_W, CELL_H = 80, 100
LAWN_XMIN, LAWN_YMIN = 40, 80
BOARD_WIDTH = 800
BOARD_HEIGHT = 600

A_REALLY_BIG_NUMBER = 100000000

# 网格坐标像素坐标转换
def grid_to_pixel(col: int, row: int) -> tuple[float, float]:
    """(col, row) -> (x, y)"""
    return col * CELL_W + LAWN_XMIN, row * CELL_H + LAWN_YMIN

def pixel_to_grid(x: float, y: float) -> tuple[int, int]:
    """(x, y) -> (col, row)"""
    return int((x - LAWN_XMIN) / CELL_W), int((y - LAWN_YMIN) / CELL_H)


# ============================================================================
# 碰撞矩形工具函数
# ============================================================================

def GetRectOverlap(r1: Rect, r2: Rect) -> int:
    """
    返回 x 轴重叠量
    正值 = 重叠量，负值 = 间距
    """
    if r1.x < r2.x:
        rmin = r1.x + r1.w
        rmax = r2.x + r2.w
        xmax = r2.x
    else:
        rmin = r2.x + r2.w
        rmax = r1.x + r1.w
        xmax = r1.x
    if rmin > xmax and rmin > rmax:
        rmin = rmax
    return int(rmin - xmax)


def GetCircleRectOverlap(x: float, y: float, r: float, rect: Rect) -> bool:
    """
    检测圆形和矩形是否重叠

    参数:
    theCircleX: 圆心X坐标
    theCircleY: 圆心Y坐标
    theRadius: 圆的半径
    theRect: 矩形对象，包含mX, mY, mWidth, mHeight属性
    """
    dx = 0  # 圆心与矩形较近一条纵边的横向距离
    dy = 0  # 圆心与矩形较近一条横边的纵向距离
    xOut = False  # 圆心横坐标是否不在矩形范围内
    yOut = False  # 圆心纵坐标是否不在矩形范围内

    if x < rect.x:
        xOut = True
        dx = rect.x - x
    elif x > rect.x + rect.w:
        xOut = True
        dx = x - rect.x - rect.w

    if y < rect.y:
        yOut = True
        dy = rect.y - y
    elif y > rect.y + rect.h:
        yOut = True
        dy = y - rect.y - rect.h

    if not xOut and not yOut:  # 如果圆心在矩形内
        return True
    elif xOut and yOut:  # 如果圆心在矩形外且在角的区域
        return dx * dx + dy * dy <= r * r
    elif xOut:  # 如果圆心仅在水平方向上超出矩形
        return dx <= r
    else:  # 如果圆心仅在垂直方向上超出矩形
        return dy <= r

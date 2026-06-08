# Vatrix-vbe-sm

 Vatrix-vbe-sm是对Pvz一代英文原版中Vasebreaker无尽关卡的python模拟，删去了所有动画、简化了豌豆子弹机制，但精确描述僵尸位置和瞬杀植物判定，以此为程序提供认知游戏的底层框架。Vatrix-vbe使得我们可以在超高算力的帮助下，向vbe可否无尽这一经典命题发起冲锋。


## About Zombie Movement

Constant：

速度参数 $γ$

动画位置 $x_{n+1}$（如撑杆n=36）

动画移动量 $s_n$（$s_n=x_{n+1}-x_n$）

动画进度增量 $δ=0.47γ/Σs$

<br/>

Variable：

时刻 $t∈N$

动画进度 $p(t)=(t+1)δ \mod 1$

当前动画 $i(t)=⌈n×p(t)⌉$（注：实际为$floor(…)+1$）

位移速度 $v(t)=(n+1)δ×s_i(t)$

<br/>

References：

https://tieba.baidu.com/p/7290751385

https://wiki.pvz1.com/doku.php?id=%E6%94%BB%E7%95%A5:%E5%83%B5%E5%B0%B8%E9%80%9F%E5%BA%A6

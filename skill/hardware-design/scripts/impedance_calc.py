#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""微带阻抗估算（IPC-2141 系近似式）——hardware-design skill 自带工具。

用法：
  python impedance_calc.py --H 0.2104 --er 4.5 --W 0.30 --T 0.035 --S 0.25 --mode diff
  python impedance_calc.py --H 0.2104 --er 4.5 --W 0.30 --mode se

仅用标准库。结果为估算值：阻焊约拉低 2~3Ω，板厂公差 ±10%，
下单前必须用板厂官方阻抗计算工具按实际层压结构复核。
"""
import argparse
import math


def z0_microstrip(h: float, w: float, t: float, er: float) -> float:
    """单端微带特征阻抗（Ω），近似式有效范围 0.1 < W/H < 2.0。"""
    if not 0.1 < w / h < 2.0:
        print(f"[警告] W/H = {w / h:.2f} 超出近似式有效范围（0.1~2.0），结果仅供参考")
    return 87.0 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))


def er_eff(er: float, h: float, w: float) -> float:
    """有效介电常数。"""
    return (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 * h / w)


def z_diff(z0: float, s: float, h: float) -> float:
    """边缘耦合差分阻抗（Ω）。"""
    return 2 * z0 * (1 - 0.48 * math.exp(-0.96 * s / h))


def main() -> None:
    p = argparse.ArgumentParser(description="微带单端/差分阻抗估算（IPC-2141 系近似式）")
    p.add_argument("--H", type=float, required=True,
                   help="介质厚度 mm（走线层到参考平面，用板厂当期层压参数）")
    p.add_argument("--er", type=float, required=True,
                   help="介电常数 Dk（用板厂公布值）")
    p.add_argument("--W", type=float, required=True, help="线宽 mm")
    p.add_argument("--T", type=float, default=0.035,
                   help="铜厚 mm（含电镀，默认 0.035 ≈ 1oz）")
    p.add_argument("--S", type=float, default=None, help="差分间距 mm（diff 模式必填）")
    p.add_argument("--mode", choices=["se", "diff"], default="se")
    a = p.parse_args()

    z0 = z0_microstrip(a.H, a.W, a.T, a.er)
    print(f"输入：H={a.H}mm  er={a.er}  W={a.W}mm  T={a.T}mm  S={a.S}mm  模式={a.mode}")
    print(f"有效介电常数 εeff ≈ {er_eff(a.er, a.H, a.W):.3f}")
    print(f"单端 Z0    ≈ {z0:.1f} Ω")
    if a.mode == "diff":
        if a.S is None:
            p.error("diff 模式需要 --S")
        zd = z_diff(z0, a.S, a.H)
        print(f"差分 Zdiff ≈ {zd:.1f} Ω")
    print()
    print("注意：①以上为估算值——阻焊约拉低 2~3Ω，板厂公差 ±10%")
    print("      ②下单前用板厂官方阻抗工具按实际层压结构复核")


if __name__ == "__main__":
    main()

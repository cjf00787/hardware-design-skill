#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IPC-2221 载流/线宽估算——hardware-design skill 自带工具。

用法：
  python trace_current.py width  --I 5   --dT 10 --layer ext --cu 1     # 电流→线宽
  python trace_current.py current --W 2  --dT 10 --layer ext --cu 1     # 线宽→电流

公式：I = k · ΔT^0.44 · A^0.725（A 单位 mil²；外层 k=0.048，内层 k=0.024）
仅用标准库。IPC-2221 为保守估算（IPC-2152 更准且更宽松）；
换层过孔经验值 0.3mm 孔径 ≈ 1.5~2A/孔，用阵列并联。
"""
import argparse
import math

K = {"ext": 0.048, "int": 0.024}
CU_OZ_TO_MIL = {1.0: 1.37, 0.5: 0.69, 2.0: 2.74}  # 1oz≈35µm、0.5oz≈17.5µm、2oz≈70µm


def area_from_current(i: float, d_t: float, layer: str) -> float:
    """由电流（A）与温升（°C）求导体截面积（mil²）。"""
    return (i / (K[layer] * d_t ** 0.44)) ** (1 / 0.725)


def current_from_area(a_mil2: float, d_t: float, layer: str) -> float:
    """由截面积（mil²）与温升（°C）求载流（A）。"""
    return K[layer] * d_t ** 0.44 * a_mil2 ** 0.725


def cu_thickness_mil(args) -> float:
    if args.cu_mil is not None:
        return args.cu_mil
    return CU_OZ_TO_MIL[args.cu]


def main() -> None:
    p = argparse.ArgumentParser(description="IPC-2221 载流/线宽估算")
    sub = p.add_subparsers(dest="mode", required=True)

    pw = sub.add_parser("width", help="由电流求线宽")
    pw.add_argument("--I", type=float, required=True, help="电流 A")
    pw.add_argument("--dT", type=float, default=10, help="允许温升 °C（默认 10）")
    pw.add_argument("--layer", choices=["ext", "int"], default="ext")
    pw.add_argument("--cu", type=float, default=1.0, choices=[0.5, 1.0, 2.0], help="铜厚 oz")
    pw.add_argument("--cu-mil", type=float, default=None, help="铜厚 mil（覆盖 --cu）")

    pc = sub.add_parser("current", help="由线宽求载流")
    pc.add_argument("--W", type=float, required=True, help="线宽 mm")
    pc.add_argument("--dT", type=float, default=10, help="目标温升 °C（默认 10）")
    pc.add_argument("--layer", choices=["ext", "int"], default="ext")
    pc.add_argument("--cu", type=float, default=1.0, choices=[0.5, 1.0, 2.0], help="铜厚 oz")
    pc.add_argument("--cu-mil", type=float, default=None, help="铜厚 mil（覆盖 --cu）")

    a = p.parse_args()
    t_mil = cu_thickness_mil(a)
    layer_name = "外层" if a.layer == "ext" else "内层"

    if a.mode == "width":
        a_mil2 = area_from_current(a.I, a.dT, a.layer)
        w_mil = a_mil2 / t_mil
        print(f"条件：I={a.I}A  ΔT={a.dT}°C  {layer_name}  铜厚={t_mil}mil（{t_mil / 1.37:.2f}oz）")
        print(f"所需截面积 A ≈ {a_mil2:.1f} mil²")
        print(f"所需线宽 W ≈ {w_mil:.1f} mil = {w_mil * 0.0254:.2f} mm")
    else:
        a_mil2 = (a.W / 0.0254) * t_mil
        i = current_from_area(a_mil2, a.dT, a.layer)
        print(f"条件：W={a.W}mm  ΔT={a.dT}°C  {layer_name}  铜厚={t_mil}mil（{t_mil / 1.37:.2f}oz）")
        print(f"截面积 A ≈ {a_mil2:.1f} mil²")
        print(f"载流 I ≈ {i:.2f} A @ ΔT={a.dT}°C")
    print()
    print("注意：①IPC-2221 为保守估算（IPC-2152 实测曲线更宽松）")
    print("      ②实际载流常由 走线+电源平面+过孔阵列 并联承担")
    print("      ③过孔经验值：0.3mm 孔径 ≈ 1.5~2A/孔")


if __name__ == "__main__":
    main()

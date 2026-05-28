"""
Geometria das ranhuras (slots) do estator e do rotor de uma maquina de inducao.
Cotas extraidas dos desenhos "DISCO DO ESTATOR" e "DISCO DO ROTOR".

A ideia: cada ranhura e definida por uma funcao que devolve o contorno (poligono)
em coordenadas LOCAIS, com:
    - x = direcao tangencial (largura da ranhura)
    - y = direcao radial (profundidade da ranhura)
    - y = 0 fica na ABERTURA (lado do entreferro) p/ o estator
      e no FUNDO (deep end) p/ o rotor -> ver comentarios.

Com o contorno em coords locais voce depois so precisa rotacionar/transladar
36x (estator) ou 28x (rotor) p/ montar a lamina inteira.

Autor: gerado p/ Bruno -- unidades em milimetros (mm).
"""

import numpy as np
import matplotlib.pyplot as plt


# --------------------------------------------------------------------------
# Helpers geometricos
# --------------------------------------------------------------------------
def arc_pts(center, R, a0, a1, n=120):
    """Pontos de um arco de raio R, do angulo a0 ao a1 (rad)."""
    a = np.linspace(a0, a1, n)
    return np.column_stack([center[0] + R * np.cos(a),
                            center[1] + R * np.sin(a)])


def tangent_from_point(P, C, R, pick="maxx"):
    """
    Ponto de tangencia na circunferencia (centro C, raio R) da reta que
    passa pelo ponto externo P. Retorna o ponto de tangencia escolhido.
    pick = 'maxx' (maior x) ou 'minx' (menor x).
    """
    P = np.asarray(P, float)
    C = np.asarray(C, float)
    d = C - P
    D = np.hypot(*d)
    if D <= R:
        raise ValueError("Ponto dentro da circunferencia.")
    L = np.sqrt(D * D - R * R)          # comprimento do segmento tangente
    base = np.arctan2(d[1], d[0])
    al = np.arcsin(R / D)
    cands = [P + L * np.array([np.cos(base + s * al), np.sin(base + s * al)])
             for s in (+1, -1)]
    return max(cands, key=lambda t: t[0]) if pick == "maxx" \
        else min(cands, key=lambda t: t[0])


# --------------------------------------------------------------------------
# RANHURA DO ESTATOR
# --------------------------------------------------------------------------
# Cotas (mm) -- do "DETALHE" no canto inferior esquerdo do desenho do estator:
#   abertura (boca):  bo = 2.800 (largura)  x  ho = 0.600 (altura)
#   cunha:            abre de 2.800 -> 5.444, parede a 22°30' (altura 0.548)
#   corpo:            paredes retas que abrem ate tangenciar o topo arredondado
#   topo:             raio R = 3.885 (semelhante a uma gota)
#   altura total:     H = 18.500
# y=0 = boca (lado do entreferro/furo). O topo arredondado e o fundo da ranhura.
STAT = dict(bo=2.800, ho=0.600, b1=5.444, hw=0.548, R=3.885, H=18.500)


def stator_slot_polygon(p=STAT):
    bo, ho = p["bo"], p["ho"]
    b1, hw = p["b1"], p["hw"]
    R, H = p["R"], p["H"]
    yc = H - R                                   # centro do arco do topo

    Ccorner = np.array([b1 / 2, ho + hw])        # canto sup. da cunha (direita)
    T = tangent_from_point(Ccorner, [0, yc], R, "maxx")
    aR = np.arctan2(T[1] - yc, T[0])             # angulo do ponto tangente dir.
    aL = np.pi - aR                              # ponto tangente esquerdo

    top = arc_pts([0, yc], R, aL, aR, 160)       # arco passando pelo topo

    pts = [[-bo / 2, 0.0],
           [-bo / 2, ho],
           [-b1 / 2, ho + hw],
           [-T[0], T[1]]]
    pts += top.tolist()
    pts += [[b1 / 2, ho + hw],
            [bo / 2, ho],
            [bo / 2, 0.0]]
    return np.array(pts), dict(T=T, yc=yc)


# --------------------------------------------------------------------------
# RANHURA DO ROTOR
# --------------------------------------------------------------------------
# Cotas (mm) -- do "DETALHE" da gota no canto inferior direito do desenho do rotor:
#   topo (lado entreferro): bico a 40° com a horizontal, largura na base 6.198
#   base do bico:           a 19.400 do fundo (logo o bico tem 22.000-19.400=2.600)
#   altura total:           H = 22.000
#   fundo (deep end):       arredondado, largura 2.031  (R = 1.0155 ~ R1 do desenho)
#   paredes retas:          de 6.198 (topo) afunilando ate o raio do fundo
#   abertura p/ entreferro: 0.600 (estreita) -- ver opcao 'opening'
# y=0 = FUNDO da ranhura; y=H = bico (lado do entreferro).
ROT = dict(wt=6.198, hb=19.400, H=22.000, wb=2.031, peak_deg=40.0, opening=0.600)


def rotor_slot_polygon(p=ROT, use_opening=True):
    wt, hb, H = p["wt"], p["hb"], p["H"]
    rb = p["wb"] / 2.0                            # raio do fundo
    apex = np.array([0.0, H])
    PR = np.array([wt / 2, hb])                   # canto da base do bico (dir.)
    Cb = np.array([0.0, rb])                      # centro do arco do fundo

    Tb = tangent_from_point(PR, Cb, rb, "maxx")   # tangencia parede->fundo
    aR = np.arctan2(Tb[1] - rb, Tb[0])
    aL = np.pi - aR
    # arco INFERIOR do fundo: de Tb_esq passando PELO FUNDO ate Tb_dir
    bottom = arc_pts(Cb, rb, aL, aR + 2 * np.pi, 120)

    if use_opening and p.get("opening"):
        # trunca a ponta do bico p/ criar a abertura estreita (boca)
        wo = p["opening"]
        # nas retas do bico, acha y onde a largura = wo
        # reta do bico (dir.): de apex(0,H) ate PR(wt/2,hb)
        t = (wo / 2) / (wt / 2)                   # fracao ao longo do bico
        y_open = H - t * (H - hb)
        top_pts = [[wo / 2, y_open], [-wo / 2, y_open]]   # boca achatada
    else:
        top_pts = [apex.tolist()]

    pts = [PR.tolist()]
    pts += top_pts                                # apex (ou boca)
    pts += [[-PR[0], PR[1]],                      # canto base do bico (esq.)
            [-Tb[0], Tb[1]]]                      # tangencia esquerda
    pts += bottom.tolist()                        # arco do fundo Tb_dir<-fundo<-Tb_esq
    return np.array(pts), dict(Tb=Tb, apex=apex)


# --------------------------------------------------------------------------
# PLOTS DETALHADOS (uma ranhura de cada, com as cotas)
# --------------------------------------------------------------------------
def annotate(ax, p1, p2, text, off=(0, 0), color="#c0392b"):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="<->", color=color, lw=1.1))
    m = ((p1[0] + p2[0]) / 2 + off[0], (p1[1] + p2[1]) / 2 + off[1])
    ax.text(m[0], m[1], text, color=color, fontsize=8.5, ha="center",
            va="center", bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))


def plot_stator():
    poly, info = stator_slot_polygon()
    fig, ax = plt.subplots(figsize=(5.2, 7.6))
    ax.fill(poly[:, 0], poly[:, 1], color="#aed6f1", ec="#1f4e79", lw=1.8)
    ax.plot(poly[:, 0], poly[:, 1], color="#1f4e79", lw=1.8)
    ax.axvline(0, color="gray", ls="-.", lw=0.7)

    bo, ho, b1, hw = STAT["bo"], STAT["ho"], STAT["b1"], STAT["hw"]
    H, R, yc = STAT["H"], STAT["R"], info["yc"]
    annotate(ax, (-bo/2, -1.4), (bo/2, -1.4), f"{bo:.3f} (boca)", (0, -0.5))
    annotate(ax, (bo/2+1.0, 0), (bo/2+1.0, ho), f"{ho:.3f}", (0.9, 0))
    annotate(ax, (-b1/2, ho+hw+0.4), (b1/2, ho+hw+0.4), f"{b1:.3f}", (0, 0.5))
    annotate(ax, (-5.6, 0), (-5.6, H), f"H = {H:.3f}", (-0.2, 0))
    ax.text(R*0.7, yc+R*0.7, f"R{R:.3f}", color="#c0392b", fontsize=8.5)
    ax.text(b1/2+0.4, ho+hw/2, "22°30'", color="#c0392b", fontsize=8)

    ax.set_title("Ranhura do ESTATOR  (36 ranhuras)\nboca no entreferro (y=0)",
                 fontsize=10)
    ax.set_xlabel("tangencial [mm]"); ax.set_ylabel("radial [mm]")
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.set_xlim(-7.5, 7.5); ax.set_ylim(-3, 20.5)
    fig.tight_layout()
    fig.savefig("ranhura_estator.png", dpi=160)
    return fig


def plot_rotor():
    poly, info = rotor_slot_polygon()
    fig, ax = plt.subplots(figsize=(4.6, 8.0))
    ax.fill(poly[:, 0], poly[:, 1], color="#f5cba7", ec="#9c4a1a", lw=1.8)
    ax.plot(poly[:, 0], poly[:, 1], color="#9c4a1a", lw=1.8)
    ax.axvline(0, color="gray", ls="-.", lw=0.7)

    wt, hb, H, wb = ROT["wt"], ROT["hb"], ROT["H"], ROT["wb"]
    annotate(ax, (-wt/2, hb+0.5), (wt/2, hb+0.5), f"{wt:.3f}", (0, 0.6))
    annotate(ax, (-wb/2, -1.2), (wb/2, -1.2), f"{wb:.3f} (fundo)", (0, -0.5))
    annotate(ax, (wt/2+1.2, 0), (wt/2+1.2, hb), f"{hb:.3f}", (1.1, 0))
    annotate(ax, (wt/2+3.0, 0), (wt/2+3.0, H), f"H = {H:.3f}", (1.1, 0))
    ax.text(-wt/2-1.6, H-1.0, "40°", color="#c0392b", fontsize=9)
    ax.text(ROT["opening"]/2+0.3, H-0.3, f"boca {ROT['opening']:.3f}",
            color="#c0392b", fontsize=7.5)

    ax.set_title("Ranhura do ROTOR  (28 ranhuras)\nbico no entreferro (y=H)",
                 fontsize=10)
    ax.set_xlabel("tangencial [mm]"); ax.set_ylabel("radial [mm]")
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.set_xlim(-6.5, 8.5); ax.set_ylim(-3, 24)
    fig.tight_layout()
    fig.savefig("ranhura_rotor.png", dpi=160)
    return fig


# --------------------------------------------------------------------------
# BONUS: monta a lamina inteira p/ conferir o encaixe (36 e 28)
# --------------------------------------------------------------------------
def place_one(poly_local, th, r_ref, mode):
    """Mapeia uma ranhura (coords locais) p/ a posicao angular th na lamina."""
    xs, ys = [], []
    for (x, y) in poly_local:
        r = (r_ref + y) if mode == "stator" else (r_ref - (ROT["H"] - y))
        ang = th + x / r                 # comprimento de arco / raio LOCAL
        xs.append(r * np.cos(ang))
        ys.append(r * np.sin(ang))
    return xs, ys


def plot_full_check():
    sp, _ = stator_slot_polygon()
    rp, _ = rotor_slot_polygon()
    r_bore = 57.5            # furo Ø115
    r_rotor = 57.0          # OD do rotor (~ furo - 2*entreferro)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.2))
    cfg = [(axes[0], sp, 36, r_bore, "stator", "#aed6f1", "#1f4e79",
            "ESTATOR - 36 ranhuras (furo Ø115, externo Ø182)", (57.5, 91.0)),
           (axes[1], rp, 28, r_rotor, "rotor", "#f5cba7", "#9c4a1a",
            "ROTOR - 28 ranhuras (OD ~Ø114)", (57.0,))]
    t = np.linspace(0, 2 * np.pi, 400)
    for ax, poly, n, r_ref, mode, fc, ec, ttl, circles in cfg:
        for k in range(n):
            th = 2 * np.pi * k / n + np.pi / 2
            xs, ys = place_one(poly, th, r_ref, mode)
            ax.fill(xs, ys, color=fc, ec=ec, lw=0.9)
        for rr in circles:
            ax.plot(rr * np.cos(t), rr * np.sin(t), "k--", lw=0.6, alpha=0.5)
        ax.set_aspect("equal"); ax.axis("off"); ax.set_title(ttl, fontsize=10)
    fig.tight_layout()
    fig.savefig("laminas_completas.png", dpi=150)
    return fig


if __name__ == "__main__":
    plot_stator()
    plot_rotor()
    plot_full_check()
    print("OK -> ranhura_estator.png, ranhura_rotor.png, laminas_completas.png")

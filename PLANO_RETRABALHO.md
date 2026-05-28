# Plano — Retrabalho para Q_s=36, Q_r=28

## Contexto
O monitor confirmou que o motor correto tem **Q_s=36 ranhuras no estator** e **Q_r=28 ranhuras no rotor** (desenho original da Fig. 1 do enunciado: "36×10°" e "28×12°51'25.714°"). Vínhamos usando Q_s=72 / Q_r=52, que eram geometrias erradas. Agora q=2 slots por fase por polo (em vez de 4), o que muda os fatores de enrolamento, as correntes e o espectro analítico. Todo o pipeline precisa ser refeito.

---

## Parâmetros novos

| Parâmetro | Valor |
|---|---|
| Q_s / Q_r | 36 / 28 |
| P / p / m | 6 / 3 / 3 |
| q (slots/fase/polo) | 2 |
| α (ângulo elétrico/ranhura) | 30° |
| kd1 | 0,9659 |
| τ (passo polar em slots) | 6 |

### Bobinas por fase por polo — conceito chave

Q_s=36 para as **3 configurações**. O q=2 (ranhuras/fase/polo) é fixo pela geometria.
O que muda é o número de **lados de bobina** por ranhura:

| Config | Camadas | Lados/ranhura | q (ranhuras/fase/polo) | Bobinas/fase/polo | N_fase |
|---|---|---|---|---|---|
| I   | Simples | 1 | 2 | 1×2 = **2** | 6×N_C  = 60  |
| II  | Dupla   | 2 | 2 | 2×2 = **4** | 12×N_C = 120 |
| III | Dupla   | 2 | 2 | 2×2 = **4** | 12×N_C = 120 |

> Config I usa camada simples → só 2 bobinas/fase/polo → Q_s=36 resolve.
> Configs II e III usam camada dupla → 4 bobinas/fase/polo (as 4 do enunciado original) → também Q_s=36, pois a segunda camada dobra os lados sem adicionar ranhuras.

### Fatores por configuração

| Config | Camadas | Passo | y1 | kp1 | kw1 | N_fase (N_C=10) | I_pk |
|---|---|---|---|---|---|---|---|
| I  | Simples | pleno | 6 | 1,0000 | 0,9659 | 6×10 = 60   | 19,40 A |
| II | Dupla   | pleno | 6 | 1,0000 | 0,9659 | 12×10 = 120 |  9,70 A |
| III| Dupla   | 5/6   | 5 | 0,9659 | 0,9330 | 12×10 = 120 | 10,05 A |

### Espectro analítico (µ→∞, B_g1=0,9 T)

B_gν = 0,9 × (kw_ν / kw1) / ν

| ν | kw_ν I/II | B_gν I/II (T) | kw_ν III | B_gν III (T) |
|---|---|---|---|---|
| 1  | 0,9659 | 0,9000 | 0,9330 | 0,9000 |
| 5  | 0,2588 | 0,0482 | 0,0670 | 0,0129 |
| 7  | 0,2588 | 0,0344 | 0,0670 | 0,0092 |
| 11 | 0,9659 | 0,0818 | 0,9330 | 0,0818 |
| 13 | 0,9659 | 0,0692 | 0,9330 | 0,0692 |

**Harmônicos de ranhura:** ν = k×(Q_s/p)±1 = k×12±1 → **ν=11, 13**, 23, 25, 35, 37...

> ⚠️ ν=11 e ν=13 são simultaneamente harmônicos de enrolamento E de ranhura. No FEMM suas amplitudes serão maiores que o analítico (soma das duas contribuições).

---

## Etapa 1 — Cálculos analíticos + relatório (itens a e b)

Atualizar `overleaf/relatorio.tex` seções a) e b):
- Novos q=2, α=30°, kd, kp, kw para as 3 configs
- Novos NI_fase, I_pk
- Nova tabela de espectro analítico
- Destacar coincidência ν=11,13 (harmônico de enrolamento E de ranhura)
- Remover referências a Q_s=72, q=4

---

## Etapa 2 — Geometria Python (geometry.py)

### Estator
- `Q_s = 36` (era 72)
- Dimensões de slot **ficam iguais** — são do desenho original Q_s=36
- `_TOOTH_ARC_S` recalcula automaticamente: 10° − 2,79° = 7,21° (era 2,21°)

### Rotor
- `Q_r = 28` (era 52)
- Remover `_SCALE_R = 28/52` — usar dimensões originais do desenho (sem escala):
  ```python
  _W_OPEN_R  = 0.600   # abertura (mm)
  _W_TOP_R   = 6.198   # largura topo (mm)
  _R_BOT_R   = 2.031/2 # raio semicírculo fundo (mm)
  _Y_FLARE_R = 2.600   # prof. flare (mm)
  _Y_BOT_R   = 22.000  # prof. total (mm)
  ```
- `_PITCH_R` = 360/28 ≈ 12,857° (recalcula automaticamente)

### Furo + chavetas
- Sem mudança (R_ri=21mm, Ø42 H7, 2×10 H7 em ±90°)

---

## Etapa 3 — Enrolamento (winding.py — reescrita total)

Período elétrico = Q_s/p = 12 slots. Nova correia (q=2):

```python
_BELT_12 = (
    [('A', +1)] * 2 +   # slots  1–2
    [('C', -1)] * 2 +   # slots  3–4
    [('B', +1)] * 2 +   # slots  5–6
    [('A', -1)] * 2 +   # slots  7–8
    [('C', +1)] * 2 +   # slots  9–10
    [('B', -1)] * 2     # slots 11–12
)
```

- `_upper(n)` → `_BELT_12[(n-1) % 12]`
- `_lower_short(n)`: passo encurtado y1=5 → `lower(n) = −upper(n−5)`
  - `ref = ((n - 5 - 1) % 36) + 1`
- Loops em `full_table()` e `_verify()` → `range(1, 37)` (era 73)

---

## Etapa 4 — main.py + analysis.py

### main.py — CONFIGS
```python
CONFIGS = {
    'I':   {'config': 1, 'kw1': 0.9659, 'N_fase': 6  * N_C},  # 60 voltas
    'II':  {'config': 2, 'kw1': 0.9659, 'N_fase': 12 * N_C},  # 120 voltas
    'III': {'config': 3, 'kw1': 0.9330, 'N_fase': 12 * N_C},  # 120 voltas
}
```

### analysis.py
- `_ANALYTICAL`: atualizar com valores da Etapa 1
- `find_slot_harmonics()`: harmônicos em ν_mec = 36M±3 (era 72M±3)
- `plot_comparison()`: adicionar ν=11, 13 ao `nu_show`
- `plot_spectrum()`: ajustar xlim para capturar slot harmonics em ν=11,13,23,25

---

## Etapa 5 — Verificação visual + FEMM

```bash
# 1. Plot Python — conferir geometria visual
~/femm_env/bin/python tools/plot_geometry.py

# 2. Regenerar .fem
DISPLAY=:1 ~/femm_env/bin/python tools/export_fem.py

# 3. Abrir FEMM GUI e conferir geometria
DISPLAY=:1 wine ~/.wine/drive_c/femm42/bin/femm.exe

# 4. Rodar simulações
DISPLAY=:1 ~/femm_env/bin/python main.py
```

---

## Etapa 6 — Resultados + relatório final

```bash
cp results/Bg_*.png results/motor_geometry_new.png \
   results/stator_geometry_new.png results/rotor_geometry_new.png overleaf/
```

- Atualizar Tab.comp com novos valores FEMM
- Atualizar texto: ke, erros FEMM vs analítico, ν=11,13 amplificados
- Destacar que ν=11,13 = sobreposição de harmônico de enrolamento + ranhura

---

## Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `geometry.py` | Q_s=36, Q_r=28, remover _SCALE_R |
| `winding.py` | Reescrita total (Q_s=36, q=2, y1=5 para III) |
| `main.py` | CONFIGS: novos kw1 e N_fase |
| `analysis.py` | _ANALYTICAL, slot harmonics, plots |
| `tools/plot_geometry.py` | Verificar se adapta automaticamente |
| `overleaf/relatorio.tex` | Seções a, b + Tab.comp + discussão |
| `models/*.fem` | Regenerados via export_fem.py |
| `results/*` + `overleaf/*.png` | Regenerados via main.py |

---

## Checklist de validação

- [ ] Configs I e II têm espectro idêntico
- [ ] Config III suprime ν=5 e ν=7 em ~73%
- [ ] ν=11 e ν=13 aparecem grandes no FEMM (winding + slot)
- [ ] Harmônicos de ranhura aparecem em ν=11,13,23,25 (não em 23,25,47,49)
- [ ] ke ≈ 1,7 (mecanismo Carter + ferro igual ao anterior)
- [ ] Relatório cabe em 4 páginas

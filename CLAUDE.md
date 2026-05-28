# Projeto FEMM — Análise Harmônica de Motor de Indução Trifásico
**UFMG | Disciplina: Conversão da Energia | Prof. Braz J. Cardoso Filho**
**Autores: Bruno Ribeiro e Arnaldo**

---

## Contexto do Projeto

Modelagem por Elementos Finitos (FEMM 4.2 via WINE no Linux) de um motor de
indução trifásico de gaiola para análise do espectro harmônico espacial da
densidade de fluxo no entreferro B_g(θ).

**Itens c) e d):** implementação FEMM + FFT (este repositório).
**Itens a) e b):** cálculo analítico em `overleaf/relatorio.tex`.

Prazo de entrega: **28/05/2026**.

---

## Estrutura de Arquivos

```
trab_femm/
├── CLAUDE.md, README.md, .gitignore
│
├── # Pipeline principal (core — ficam na raiz)
├── main.py       ← orquestrador (roda as 3 configs, salva em results/)
├── geometry.py   ← desenha geometria no FEMM (estator + rotor + chavetas)
├── materials.py  ← materiais, circuitos e block labels
├── winding.py    ← tabelas de atribuição de ranhuras (sem FEMM)
├── solver.py     ← malha, solver, extração de B_g
├── analysis.py   ← FFT espacial, normalização e plots
│
├── models/       ← .fem prontos para abrir no FEMM GUI
│   ├── motor_config_I/II/III.fem
│   └── Motor_Passo_Encurtado_Vanucci.FEM (referência)
│
├── results/      ← saídas de simulação e figuras de geometria
│   ├── Bg_config_I/II/III.csv
│   ├── Bg_spatial_I/II/III.png
│   ├── Bg_spectrum_I/II/III.png
│   ├── Bg_comparison.png
│   ├── motor_field_color_I/II/III.png
│   ├── motor_geometry_new.png    ← motor completo (estator + rotor + chavetas)
│   ├── stator_geometry_new.png
│   └── rotor_geometry_new.png
│
├── tools/        ← scripts auxiliares (todos usam results/ como saída)
│   ├── plot_geometry.py     ← figuras matplotlib (sem FEMM)
│   ├── field_plot.py        ← mapa |B| a partir do .ans
│   ├── export_fem.py        ← regenera models/*.fem
│   ├── check_geometry.py    ← screenshot FEMM para comparação
│   ├── motor_3d.py          ← vista 3D ilustrativa
│   └── linear_iron_test.py  ← diagnóstico ferro linear µ_r=5000
│
├── docs/         ← especificações e referências
│   ├── motor_femm_spec.md
│   ├── Projeto FEMM - 2026-1.pdf
│   ├── rotor_drawing.jpg
│   └── rotor_certo/  ← desenho técnico rotor 52 ranhuras
│
├── legacy/       ← arquivos antigos isolados (não usar)
│   ├── main.tex, motor_3d.png
│   ├── motor_field_I/II/III.png (bitmaps FEMM antigos)
│   └── Bg_linear_I.csv, Bg_spectrum_linear_I.png
│
└── overleaf/     ← relatório LaTeX (entrega)
    ├── relatorio.tex
    └── *.png (cópias para compilação — atualizar após main.py)
```

Arquivos `.ans` (soluções FEMM) ficam em `/tmp/femm_work/` (ignorados pelo git).

---

## Como Rodar

```bash
cd "/home/ribb/Área de trabalho/ufmg/trab_femm"
DISPLAY=:1 ~/femm_env/bin/python main.py
```

Virtualenv Python: `~/femm_env`
FEMM: `~/.wine/drive_c/femm42/bin/femm.exe`

### Abrir modelo FEMM diretamente

```bash
DISPLAY=:1 wine ~/.wine/drive_c/femm42/bin/femm.exe \
  "/home/ribb/Área de trabalho/ufmg/trab_femm/models/motor_config_I.fem"
```

Depois: F8 para Solve, F9 para Post-Processor.

---

## Parâmetros da Máquina

| Parâmetro | Valor |
|---|---|
| Polos P / pares p | 6 / 3 |
| Fases m | 3 |
| Ranhuras estator Q_s | 36 |
| Ranhuras rotor Q_r | 28 |
| Ranhuras/polo/fase q | 2 |
| Entreferro g | 0,50 mm |
| Tensão terminal | 127 V_rms / 60 Hz |
| Aço | M250-50A (APERAM E105) |
| B_g1 alvo | 0,9 T |
| Comprimento do pacote L | 140 mm |

---

## Configurações de Enrolamento

| Config | Camadas | Passo | k_w1 | N_fase | I_pk (A) |
|---|---|---|---|---|---|
| I  | Simples | pleno (y1=6) | 0,9659 | 60  | 19,41 |
| II | Dupla   | pleno (y1=6) | 0,9659 | 120 | 9,71  |
| III| Dupla   | 5/6 (y1=5)  | 0,9330 | 120 | 10,05 |

Excitação em t=0: i_A = I_pk, i_B = i_C = −I_pk/2

---

## Resultados Finais (B_g1 = 0,9 T) — Q_s=36, Q_r=28

| ν | Config I | Config II | Config III | Analítico I/II | Analítico III |
|---|---|---|---|---|---|
| 1  | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T |
| 5  | 0,0413 T | 0,0413 T | **0,0113 T** | 0,0482 T | 0,0129 T |
| 7  | 0,0327 T | 0,0327 T | **0,0092 T** | 0,0344 T | 0,0092 T |
| **11** | **0,2225 T** | **0,2225 T** | **0,2224 T** | 0,0818 T | 0,0818 T |
| 13 | 0,0711 T | 0,0711 T | 0,0711 T | 0,0692 T | 0,0692 T |
| 23 | 0,1207 T | 0,1207 T | 0,1206 T | — | — |
| 25 | 0,0851 T | 0,0851 T | 0,0849 T | — | — |
| 35 | 0,0522 T | 0,0522 T | 0,0525 T | — | — |
| 37 | 0,0571 T | 0,0571 T | 0,0570 T | — | — |

ν=11 (24,7% de B_g1): harmônico de ranhura dominante — simultaneamente
harmônico de enrolamento E de ranhura (ν=12×1−1=11), muito amplificado pela
permeância de ranhura.
Slot harmonics: ν = k·(Q_s/p)±1 = k·12±1 → 11, 13, 23, 25, 35, 37...
Config III reduz ν=5,7 mas NÃO ν=11,13 (independem do passo de enrolamento).

---

## Geometria FEMM

Dois círculos explícitos (R_bound=110mm, R_se=91,4mm) + furo do eixo com
chavetas. Superfícies de estator/rotor formadas por arcos e linhas radiais
(sem `mi_drawarc` por ranhura — evita bug de raio do FEMM).

| Região | Raio(es) | Notas |
|---|---|---|
| Fronteira BC | 110,0 mm | A=0 |
| Estator externo | 91,4 mm | círculo explícito |
| Estator interno | 57,5 mm | formado por arcos de ranhura |
| Rotor externo | 57,0 mm | formado por arcos de barra |
| Furo do eixo | 21,0 mm + chavetas | arcos + filetes R1 |

**Ranhuras estator:** semi-fechadas, pescoço 2,8mm, cunha 22°30' (h=0,548mm), corpo com arco R3,885mm (~190° split em 2×95°)
**Barras rotor:** semi-fechadas, abertura 0,600mm, bico 40°/2,6mm, trapézio + semicírculo R1,0155mm (nativo, sem escala)
**Furo:** Ø42 H7 com 2 rasgos de chaveta 10 H7 em ±90°, filetes R1

---

## Decisões de Implementação

### Bug crítico (arco >180° no FEMM)
`mi_drawarc` com ângulo ~190° (fundo da ranhura estator) confunde detecção de
regiões do FEMM → "Material properties have not been defined for all regions".
Fix: ponto intermediário P5 (deepest point) divide em dois arcos de ~95°.

### Config III — labels duplicados
Slots mistos (2 fases por slot) com 2 block labels no mesmo region geram warning.
Fix: circuito único `NC3` com turns = net_factor × N_c × I_pk por slot.

### Fator de escala (Carter + ferro)
FEMM com M250-50A dá B_g1 ≈ 0,68 T vs 0,9 T analítico → ke≈1,33.
Código aplica escala automática após cada simulação (mantém espectro de forma).

### Rasgos de chaveta no furo
Furo Ø42 desenhado como 3 arcos CCW separados por 2 rasgos retangulares.
Filetes R1 desenhados como arcos CCW invertidos (start/end trocados).
ke permanece 1,733 — rasgos em r=21–25mm, longe do entreferro em r=57mm.

### Path com caractere especial
`Área de trabalho` tem `Á` → Wine falha ao criar `.ans`.
Fix: arquivos de trabalho em `/tmp/femm_work/` (ASCII puro).
Modelos `.fem` prontos ficam em `models/` (copiados via shutil).

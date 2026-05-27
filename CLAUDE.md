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
| Ranhuras estator Q_s | 72 |
| Ranhuras rotor Q_r | 52 |
| Entreferro g | 0,50 mm |
| Tensão terminal | 127 V_rms / 60 Hz |
| Aço | M250-50A (APERAM E105) |
| B_g1 alvo | 0,9 T |
| Comprimento do pacote L | 140 mm |

---

## Configurações de Enrolamento

| Config | Camadas | Passo | k_w1 | N_fase | I_pk (A) |
|---|---|---|---|---|---|
| I  | Simples | pleno (y1=12) | 0,9577 | 120 | 9,79 |
| II | Dupla   | pleno (y1=12) | 0,9577 | 240 | 4,90 |
| III| Dupla   | 5/6 (y1=10)  | 0,9250 | 240 | 5,07 |

Excitação em t=0: i_A = I_pk, i_B = i_C = −I_pk/2

---

## Resultados Finais (B_g1 = 0,9 T) — Q_r=52

| ν | Config I | Config II | Config III | Analítico I/II | Analítico III |
|---|---|---|---|---|---|
| 1  | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T |
| 5  | 0,0179 T | 0,0179 T | **0,0036 T** | 0,0386 T | 0,0103 T |
| 7  | 0,0130 T | 0,0130 T | **0,0031 T** | 0,0212 T | 0,0057 T |
| 11 | 0,0061 T | 0,0061 T | 0,0058 T | 0,0108 T | 0,0108 T |
| 13 | 0,0054 T | 0,0054 T | 0,0051 T | 0,0091 T | 0,0091 T |
| **23** | **0,2706 T** | **0,2706 T** | **0,2705 T** | — | — |
| **25** | **0,2186 T** | **0,2186 T** | **0,2187 T** | — | — |
| 47 | 0,0246 T | 0,0246 T | 0,0246 T | — | — |
| 49 | 0,0356 T | 0,0356 T | 0,0355 T | — | — |
| 71 | 0,0510 T | 0,0510 T | 0,0511 T | — | — |
| 73 | 0,0462 T | 0,0462 T | 0,0462 T | — | — |

ν=23 (30,1% de B_g1) e ν=25 (24,3%): harmônicos de ranhura principais.
ν = k·(Q_s/p)±1 = k·24±1, independem de Q_r e do tipo de enrolamento.

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

**Ranhuras estator:** semi-fechadas, pescoço 2,8mm, corpo trapezoidal, arco R3,885mm
**Barras rotor:** semi-fechadas, abertura 0,323mm, trapezoidal + semicírculo (escala 28/52)
**Furo:** Ø42 H7 com 2 rasgos de chaveta 10 H7 em ±90°, filetes R1

---

## Decisões de Implementação

### Bug crítico (arco com raio errado)
`mi_drawarc(x1,y1,x2,y2,angle,1)` calcula `r = corda / (2·sin(angle/2))`.
Para ângulos pequenos com corda pequena (ranhura estreita), o raio fica errado.
Fix: círculos concêntricos + linhas radiais; nenhum `mi_drawarc` por ranhura individual.

### Config III — labels duplicados
Slots mistos (2 fases por slot) com 2 block labels no mesmo region geram warning.
Fix: circuito único `NC3` com turns = net_factor × N_c × I_pk por slot.

### Fator de escala (Carter + ferro)
FEMM com M250-50A dá B_g1 ≈ 0,52 T vs 0,9 T analítico → ke=1,73.
Código aplica escala automática após cada simulação (mantém espectro de forma).

### Rasgos de chaveta no furo
Furo Ø42 desenhado como 3 arcos CCW separados por 2 rasgos retangulares.
Filetes R1 desenhados como arcos CCW invertidos (start/end trocados).
ke permanece 1,733 — rasgos em r=21–25mm, longe do entreferro em r=57mm.

### Path com caractere especial
`Área de trabalho` tem `Á` → Wine falha ao criar `.ans`.
Fix: arquivos de trabalho em `/tmp/femm_work/` (ASCII puro).
Modelos `.fem` prontos ficam em `models/` (copiados via shutil).

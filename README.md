# Análise Harmônica de Motor de Indução por Elementos Finitos

**UFMG — Conversão de Energia Elétrica e Mecânica**
**Prof. Braz J. Cardoso Filho**
**Autores:** Bruno Ribeiro e Arnaldo

---

## Contexto

Modelagem por Elementos Finitos (FEMM 4.2) de um motor de indução trifásico de
gaiola para análise do espectro harmônico espacial da densidade de fluxo no
entreferro B_g(θ). Três configurações de enrolamento são comparadas entre si e
com cálculo analítico — itens **c) e d)** do enunciado. Os itens a) e b)
(cálculo analítico) estão em `overleaf/relatorio.tex`.

---

## Especificações

| Parâmetro | Valor |
|---|---|
| Polos *P* / pares *p* | 6 / 3 |
| Fases *m* | 3 |
| Ranhuras estator *Q_s* | 72 |
| Ranhuras rotor *Q_r* | 52 |
| Entreferro *g* | 0,50 mm |
| Tensão de fase | 127 V_rms / 60 Hz |
| Aço laminado | M250-50A (APERAM E105) |
| *B*_g1 alvo | 0,9 T |
| Comprimento axial *L* | 140 mm |

### Configurações de Enrolamento

| Config | Camadas | Passo | *k*_w1 | *N*_fase | *I*_pk (A) |
|---|---|---|---|---|---|
| I   | Simples | pleno (*y₁*=12) | 0,9577 | 120 | 9,79 |
| II  | Dupla   | pleno (*y₁*=12) | 0,9577 | 240 | 4,90 |
| III | Dupla   | 5/6  (*y₁*=10)  | 0,9250 | 240 | 5,07 |

---

## Estrutura do Repositório

```
trab_femm/
│
├── main.py          ← orquestrador: roda as 3 configs em sequência
├── geometry.py      ← desenha a geometria no FEMM
├── materials.py     ← materiais, circuitos e block labels
├── winding.py       ← tabelas de atribuição de ranhuras
├── solver.py        ← malha, solver e extração de B_g(θ)
├── analysis.py      ← FFT espacial, normalização e plots
│
├── models/          ← modelos FEMM prontos para abrir no GUI
│   ├── motor_config_I.fem
│   ├── motor_config_II.fem
│   ├── motor_config_III.fem
│   └── Motor_Passo_Encurtado_Vanucci.FEM  (referência)
│
├── results/         ← saídas das simulações (CSV + PNG)
│   ├── Bg_config_I/II/III.csv
│   ├── Bg_spatial_I/II/III.png
│   ├── Bg_spectrum_I/II/III.png
│   ├── Bg_comparison.png
│   ├── motor_field_color_I/II/III.png
│   ├── motor_geometry_new.png
│   ├── stator_geometry_new.png
│   └── rotor_geometry_new.png
│
├── tools/           ← scripts auxiliares e de visualização
│   ├── plot_geometry.py     ← gera figuras de geometria (matplotlib)
│   ├── field_plot.py        ← mapa de |B| a partir do .ans
│   ├── export_fem.py        ← regenera os .fem em models/
│   ├── check_geometry.py    ← compara geometria FEMM vs Python
│   ├── motor_3d.py          ← vista 3D ilustrativa
│   └── linear_iron_test.py  ← diagnóstico ferro linear
│
├── docs/            ← especificações e referências
│   ├── motor_femm_spec.md
│   ├── Projeto FEMM - 2026-1.pdf
│   ├── rotor_drawing.jpg
│   └── rotor_certo/         ← desenho técnico rotor 52 ranhuras
│
├── legacy/          ← arquivos antigos / diagnóstico isolados
│   ├── main.tex             (rascunho analítico — ver overleaf/)
│   ├── motor_field_I/II/III.png  (bitmaps antigos do FEMM)
│   ├── Bg_linear_I.csv      (diagnóstico Q_r=56)
│   └── Bg_spectrum_linear_I.png
│
└── overleaf/        ← relatório LaTeX (entrega final)
    ├── relatorio.tex
    └── *.png        (cópias das figuras para compilação)
```

---

## Como Executar

### Pré-requisitos

```bash
# Python virtual env com pyFEMM
~/femm_env/bin/python -m pip install pyFEMM numpy matplotlib pillow

# FEMM 4.2 via Wine
# Caminho esperado: ~/.wine/drive_c/femm42/bin/femm.exe
```

> **Atenção:** `Área de trabalho` contém `Á` — o Wine rejeita paths não-ASCII
> para salvar `.ans`. Os arquivos de trabalho ficam em `/tmp/femm_work/`.

---

### Rodar todas as simulações (Python)

```bash
cd "/home/ribb/Área de trabalho/ufmg/trab_femm"
DISPLAY=:1 ~/femm_env/bin/python main.py
```

Gera em `results/`: CSVs, `Bg_spatial_*.png`, `Bg_spectrum_*.png`, `Bg_comparison.png`.

---

### Abrir um modelo direto no FEMM GUI (sem Python)

**Opção 1 — via terminal (abre e já carrega o arquivo):**

```bash
DISPLAY=:1 wine ~/.wine/drive_c/femm42/bin/femm.exe \
  "/home/ribb/Área de trabalho/ufmg/trab_femm/models/motor_config_I.fem"
```

**Opção 2 — abrir o FEMM e navegar:**

```bash
DISPLAY=:1 wine ~/.wine/drive_c/femm42/bin/femm.exe
```

Depois: **File → Open** → navegar até `models/motor_config_I.fem`

Para resolver: **Solve → Run** (atalho `F8`)
Para ver o campo: **Solve → Post-Processor** (atalho `F9`)

**Os três modelos disponíveis:**

| Arquivo | Config | Enrolamento | *I*_pk |
|---|---|---|---|
| `models/motor_config_I.fem` | I | Simples, passo pleno | 9,79 A |
| `models/motor_config_II.fem` | II | Dupla, passo pleno | 4,90 A |
| `models/motor_config_III.fem` | III | Dupla, 5/6 encurtado | 5,07 A |

---

### Outras tarefas

```bash
# Figuras de geometria (sem FEMM, só matplotlib)
~/femm_env/bin/python tools/plot_geometry.py
# → results/motor_geometry_new.png, stator_geometry_new.png, rotor_geometry_new.png

# Verificar geometria FEMM vs Python
DISPLAY=:1 ~/femm_env/bin/python tools/check_geometry.py
# → results/femm_geometry_check.png

# Regenerar modelos .fem em models/
DISPLAY=:1 ~/femm_env/bin/python tools/export_fem.py

# Mapa de campo |B| (requer .ans em /tmp/femm_work/ — rodar main.py antes)
DISPLAY=:1 ~/femm_env/bin/python tools/field_plot.py
# → results/motor_field_color_I/II/III.png

# Atualizar figuras no Overleaf após nova simulação
cp results/Bg_spatial_*.png results/Bg_spectrum_*.png results/Bg_comparison.png \
   results/motor_geometry_new.png results/stator_geometry_new.png \
   results/rotor_geometry_new.png overleaf/
```

---

## Resultados — Espectro Harmônico (B_g1 = 0,9 T)

| ν | Config I | Config II | Config III | Analítico I/II | Analítico III |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1   | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T |
| 5   | 0,0179 T | 0,0179 T | **0,0036 T** | 0,0386 T | 0,0103 T |
| 7   | 0,0130 T | 0,0130 T | **0,0031 T** | 0,0212 T | 0,0057 T |
| 11  | 0,0061 T | 0,0061 T | 0,0058 T | 0,0108 T | 0,0108 T |
| 13  | 0,0054 T | 0,0054 T | 0,0051 T | 0,0091 T | 0,0091 T |
| **23** | **0,2706 T** | **0,2706 T** | **0,2705 T** | — | — |
| **25** | **0,2186 T** | **0,2186 T** | **0,2187 T** | — | — |
| 47  | 0,0246 T | 0,0246 T | 0,0246 T | — | — |
| 49  | 0,0356 T | 0,0356 T | 0,0355 T | — | — |
| 71  | 0,0510 T | 0,0510 T | 0,0511 T | — | — |
| 73  | 0,0462 T | 0,0462 T | 0,0462 T | — | — |

ν = k·(Q_s/p) ± 1 = k·24 ± 1 → harmônicos de ranhura, independem do enrolamento.

**Observações:**
- Configs I e II são eletromagneticamente idênticas ✓
- Config III atenua ν=5 em ~80% e ν=7 em ~76% vs passo pleno ✓
- Fator de escala ke ≈ 1,73 (Carter + relutância finita do ferro)
- B_g1 bruto: ≈ 0,52 T antes da normalização

---

## Decisões de Implementação

| Decisão | Motivo |
|---|---|
| Geometria por linhas radiais + arcos (sem `mi_drawarc` por ranhura) | Bug do FEMM: `mi_drawarc` com ângulo pequeno calcula raio errado pela corda |
| Chavetas no furo via arcos CCW invertidos (geometry.py) | Fiel ao desenho técnico; ke não muda (chavetas em r=21–25mm, longe do entreferro em r=57mm) |
| Config III: circuito único `NC3` com turns = net_AT | Dois block labels na mesma região geram warning e resultado errado |
| Escala pós-hoc ke = B_g1_alvo / B_g1_FEMM | Carter + ferro produzem B ≈ 40% menor que analítico |
| Arquivos `.fem`/`.ans` de trabalho em `/tmp/femm_work/` | Path `Área de trabalho` com `Á` é rejeitado pelo Wine |

---

## Dependências

| Pacote | Versão testada |
|---|---|
| Python | 3.12 |
| pyFEMM | ≥ 0.0.4 |
| numpy | ≥ 1.26 |
| matplotlib | ≥ 3.8 |
| Pillow | ≥ 10.0 |
| FEMM | 4.2 (via Wine 9.x) |

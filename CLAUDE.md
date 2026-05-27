# Projeto FEMM — Análise Harmônica de Motor de Indução Trifásico
**UFMG | Disciplina: Conversão da Energia | Prof. Braz J. Cardoso Filho**
**Autores: Bruno Ribeiro e Arnaldo**

---

## Contexto do Projeto

Modelagem por Elementos Finitos (FEMM 4.2 via WINE no Linux) de um motor de
indução trifásico de gaiola para análise do espectro harmônico espacial da
densidade de fluxo no entreferro B_g(θ).

**O que foi implementado:** itens c) e d) do enunciado (FEMM + FFT).
**O que está no LaTeX (main.tex):** itens a) e b) (cálculo analítico).

---

## Estrutura de Arquivos

```
trab_femm/
├── CLAUDE.md              ← este arquivo
├── motor_femm_spec.md     ← especificação detalhada (geometria, enrolamentos, calibração)
├── main.tex               ← parte analítica (itens a e b)
├── Projeto FEMM - 2026-1.pdf ← enunciado original
│
├── winding.py             ← tabelas de atribuição de ranhuras (sem FEMM)
├── geometry.py            ← desenho da geometria no FEMM
├── materials.py           ← materiais, circuitos e labels de bloco
├── solver.py              ← malha, solver, extração de B_g
├── analysis.py            ← FFT espacial e gráficos
├── main.py                ← orquestrador das 3 configurações
│
├── Bg_config_I.csv        ← B_g(θ) Config I  (720 pontos, escalado para B_g1=0.9T)
├── Bg_config_II.csv       ← B_g(θ) Config II
├── Bg_config_III.csv      ← B_g(θ) Config III
├── Bg_spatial_I.png       ← distribuição espacial Config I
├── Bg_spatial_II.png
├── Bg_spatial_III.png
├── Bg_spectrum_I.png      ← espectro harmônico Config I
├── Bg_spectrum_II.png
├── Bg_spectrum_III.png
└── Bg_comparison.png      ← comparação das 3 configs
```

Arquivos `.fem` e `.ans` (temporários do FEMM): `/tmp/femm_work/`

---

## Como Rodar

```bash
cd "/home/ribb/Área de trabalho/ufmg/trab_femm"
DISPLAY=:1 ~/femm_env/bin/python main.py
```

Virtualenv Python: `~/femm_env`
FEMM path: `~/.wine/drive_c/femm42/bin/femm.exe`

---

## Parâmetros da Máquina

| Parâmetro | Valor |
|---|---|
| Polos P | 6 |
| Fases m | 3 |
| Ranhuras do estator Q_s | 72 |
| Ranhuras do rotor Q_r | 52 |
| Entreferro g | 0,50 mm |
| Tensão terminal | 127 V_rms / 60 Hz |
| Aço | M250-50A (APERAM E105) |
| B_g1 alvo | 0,9 T |
| Comprimento do pacote L | 140 mm |

---

## Configurações de Enrolamento

| Config | Camadas | Passo | k_w1 | N_fase | I_pk (A) |
|---|---|---|---|---|---|
| I | Simples | pleno (y1=12) | 0,9577 | 120 | 9,79 |
| II | Dupla | pleno (y1=12) | 0,9577 | 240 | 4,90 |
| III | Dupla | 5/6 (y1=10) | 0,9250 | 240 | 5,07 |

Excitação em t=0: i_A = I_pk, i_B = i_C = −I_pk/2

---

## Resultados Finais (B_g1 normalizado para 0,9 T) — Q_r=52

| ν | Config I | Config II | Config III | Analítico I/II | Analítico III |
|---|---|---|---|---|---|
| 1 | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T |
| 5 | 0,0179 T | 0,0179 T | **0,0036 T** | 0,0386 T | 0,0103 T |
| 7 | 0,0130 T | 0,0130 T | **0,0031 T** | 0,0212 T | 0,0057 T |
| 11 | 0,0061 T | 0,0061 T | 0,0058 T | 0,0108 T | 0,0108 T |
| 13 | 0,0054 T | 0,0054 T | 0,0051 T | 0,0091 T | 0,0091 T |
| **23** | **0,2706 T** | **0,2706 T** | **0,2705 T** | — | — |
| **25** | **0,2186 T** | **0,2186 T** | **0,2187 T** | — | — |
| 47 | 0,0246 T | 0,0246 T | 0,0246 T | — | — |
| 49 | 0,0356 T | 0,0356 T | 0,0355 T | — | — |
| 71 | 0,0510 T | 0,0510 T | 0,0511 T | — | — |
| 73 | 0,0462 T | 0,0462 T | 0,0462 T | — | — |

**Harmônicos de ranhura do estator:** ν=23 (30,1% de B_g1) e ν=25 (24,3% de B_g1)
Determinados por ν = k·(Q_s/p)±1 = k·24±1, independente de Q_r.
Família M=3: ν=71 (5,7%) e ν=73 (5,1%) também visíveis.

**Observações importantes:**
- Config III atenua ν=5 em ~80% e ν=7 em ~76% vs passo pleno ✓
- Config I e II são idênticas eletromagneticamente ✓
- Harmônicos de ranhura (ν=23,25,47,49,71,73) **não se alteram** entre configs ✓
- Fator de escala aplicado: ×1,732 (Carter + permeabilidade finita do ferro)
- B_g1 bruto (sem normalização): 0,5195 T
- ke caiu de 2,00→1,73 em relação a Q_r=56 (abertura de ranhura do rotor menor)

---

## Geometria FEMM

7 círculos concêntricos + linhas radiais (sem arcos por ranhura — evita bug de raio):

| Círculo | Raio (mm) | Propósito |
|---|---|---|
| R_bound | 110,0 | fronteira BC A=0 |
| R_se | 91,4 | face externa do estator |
| R_slot_crown | 76,6 | topo das ranhuras / base da coroa |
| R_si | 57,5 | furo do estator |
| R_re | 57,0 | face externa do rotor |
| R_bar_bot | 37,6 | fundo das barras do rotor |
| R_ri | 30,0 | eixo |

Linhas radiais: 72×2 para ranhuras do estator, 56×2 para barras do rotor.
Largura angular das ranhuras: delta_s = arcsin(w_so/2 / R_si) = arcsin(0,8/57,5) ≈ 0,796°
Largura angular das barras: delta_r = arcsin(w_r_top/2 / R_re) = arcsin(1,375/57) ≈ 1,38°

**Regiões rotuladas:** ~261 block labels (1 ar externo + 1 coroa + 72 dentes + 72 ranhuras + 1 entreferro + 56 barras + 56 ferro rotor + 1 coroa rotor + 1 eixo)

---

## Decisões de Implementação

### Bug crítico corrigido (arco com raio errado)
`mi_drawarc(x1,y1,x2,y2,angle,1)` no FEMM calcula o raio pela fórmula
`r = corda / (2·sin(angle/2))`. Se o ângulo for 5° mas a corda for 3mm
(para slot de 3mm de largura a R=76mm), o FEMM desenhava arco de raio ~34mm
em vez de ~76mm. Fix: usar círculos explícitos + linhas radiais (sem arcos por slot).

### Config III — labels duplicados
Config III tem slots "mistos" (2 fases diferentes por slot). Colocar 2 block labels
no mesmo region gerava warning e resultados errados. Fix: usar um único circuito
'NC3' com I=1 A e turns = round(net_factor × N_c × I_pk) por slot.

### Fator de escala (Carter + ferro)
A fórmula analítica assume μ_ferro→∞ e furo liso. O FEMM com M250-50A e
aberturas de ranhura de 1,6 mm produz B_g1 ~40% menor (fator de Carter ≈ 1,67).
O código aplica escala automática: kc = 0,9 / B_g1_medido após cada simulação.

### Path com caractere especial
`Área de trabalho` tem `Á` → WINE falha ao criar `.ans`. Fix: todos os arquivos
`.fem`/`.ans` salvos em `/tmp/femm_work/` (ASCII puro).

---

## Próximas Etapas (Etapa 3 — Relatório)

1. Incluir plots `Bg_spatial_*.png` e `Bg_comparison.png` no LaTeX
2. Comparar tabela de resultados FEMM com tabela analítica (já no main.tex)
3. Discutir fator de Carter e harmônicos de ranhura ν=23,25
4. Item d): identificar harmônico fundamental de ranhura = ν=23 em todos os casos
5. Entregar até 28/05/2026

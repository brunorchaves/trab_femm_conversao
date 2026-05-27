# Análise Harmônica de Motor de Indução por Elementos Finitos

**UFMG — Conversão de Energia Elétrica e Mecânica**  
**Prof. Braz J. Cardoso Filho**  
**Autores:** Bruno Ribeiro e Arnaldo

---

## Contexto

Modelagem por Elementos Finitos (FEMM 4.2) de um motor de indução trifásico de gaiola para análise do espectro harmônico espacial da densidade de fluxo no entreferro $B_g(\theta)$. Três configurações de enrolamento são comparadas entre si e com cálculo analítico.

Corresponde aos **itens c) e d)** do enunciado (*Projeto FEMM - 2026-1.pdf*). Os itens a) e b) (cálculo analítico) estão em `overleaf/relatorio.tex`.

---

## Especificações da Máquina

| Parâmetro | Valor |
|---|---|
| Polos *P* | 6 |
| Fases *m* | 3 |
| Ranhuras estator *Q_s* | 72 |
| Ranhuras rotor *Q_r* | 52 |
| Entreferro *g* | 0,50 mm |
| Tensão de fase | 127 V_rms / 60 Hz |
| Aço laminado | M250-50A (APERAM E105) |
| *B*_g1 alvo | 0,9 T |
| Comprimento axial *L* | 140 mm |

### Geometria do estator
Ranhura semi-fechada, perfil trapezoidal com arco de fundo — `R_si` = 57,5 mm, `R_se` = 91,4 mm,
abertura `w_o` = 2,8 mm, profundidade `h_s` = 18,5 mm.

### Geometria do rotor
Ranhura semi-fechada, perfil trapezoidal com semicírculo no fundo, escalonada do desenho original de 28 ranhuras (fator 28/52) — `R_re` = 57,0 mm, `R_ri` = 21,0 mm (Ø42 H7 + 2 rasgos de chaveta 10 H7 @ 180°).

---

## Configurações de Enrolamento

| Config | Camadas | Passo | *k*_w1 | *N*_fase | *I*_pk (A) |
|---|---|---|---|---|---|
| I   | Simples | pleno (*y*₁ = 12) | 0,9577 | 120 | 9,79 |
| II  | Dupla   | pleno (*y*₁ = 12) | 0,9577 | 240 | 4,90 |
| III | Dupla   | 5/6 (*y*₁ = 10)   | 0,9250 | 240 | 5,07 |

Excitação em *t* = 0: *i*_A = *I*_pk, *i*_B = *i*_C = −*I*_pk/2.

---

## Estrutura do Repositório

```
trab_femm/
│
├── # Pipeline de simulação FEMM
├── main.py              ← orquestrador: roda as 3 configs em sequência
├── geometry.py          ← desenha a geometria no FEMM (ranhuras, barras)
├── materials.py         ← materiais, circuitos e block labels
├── winding.py           ← tabelas de atribuição de ranhuras (sem FEMM)
├── solver.py            ← malha, solver e extração de B_g(θ)
├── analysis.py          ← FFT espacial, normalização e plots
│
├── # Visualização (matplotlib, sem FEMM)
├── plot_geometry.py     ← seção transversal completa (estator + rotor)
├── field_plot.py        ← mapa de |B| em grade 2D a partir do .ans
├── motor_3d.py          ← vista 3D em corte (ilustrativa)
├── linear_iron_test.py  ← diagnóstico ferro linear (µ_r = 5 000)
│
├── # Resultados numéricos
├── Bg_config_I.csv      ← B_g(θ) Config I  — 720 pontos, B_g1 = 0,9 T
├── Bg_config_II.csv
├── Bg_config_III.csv
├── Bg_linear_I.csv      ← Config I com ferro linear (diagnóstico)
│
├── # Figuras de resultados
├── Bg_spatial_I/II/III.png     ← distribuição espacial B_g(θ)
├── Bg_spectrum_I/II/III.png    ← espectro harmônico |B_ν|
├── Bg_spectrum_linear_I.png    ← espectro diagnóstico ferro linear
├── Bg_comparison.png           ← comparação das 3 configs
├── motor_field_I/II/III.png    ← bitmap de campo (via FEMM)
├── motor_field_color_I/II/III.png ← mapa |B| via grade Python
│
├── # Figuras de geometria
├── motor_geometry_new.png   ← motor completo (estator + rotor + furo)
├── rotor_geometry_new.png   ← rotor: seção completa + detalhe 4 barras
├── stator_geometry_new.png  ← estator: seção completa + detalhe 4 ranhuras
├── motor_3d.png
│
├── # Relatório (Overleaf)
├── overleaf/
│   ├── relatorio.tex        ← relatório principal (itens a–d)
│   ├── slot_geometry.png
│   ├── Bg_*.png             ← cópias para o Overleaf
│
├── # Referência — rotor 52 ranhuras (desenho técnico)
├── rotor_certo/
│   ├── rotor_52.py                  ← script de plotagem/dimensionamento
│   ├── rotor_52_ranhuras.png
│   ├── rotor_52_detalhe_ranhura.png
│   └── rotor_52_detalhe_furo.png
│
├── # Documentação e arquivos de referência
├── motor_femm_spec.md          ← especificação detalhada da geometria
├── Projeto FEMM - 2026-1.pdf   ← enunciado original
├── rotor_drawing.jpg           ← foto do desenho técnico do rotor
├── Motor_Passo_Encurtado_Vanucci.FEM  ← modelo FEMM de referência
├── motor_config_I/II/III.fem   ← modelos FEMM gerados
├── motor_config_I/II/III.ans   ← soluções FEMM
│
└── main.tex                    ← parte analítica (itens a e b)
```

---

## Como Executar

### Pré-requisitos

```bash
# Python virtualenv com pyFEMM
~/femm_env/bin/python -m pip install pyFEMM numpy matplotlib

# FEMM 4.2 via Wine
# Caminho esperado: ~/.wine/drive_c/femm42/bin/femm.exe
```

> **Atenção — path com caractere especial:** `Área de trabalho` contém `Á`.
> O Wine falha ao criar `.ans` em paths não-ASCII. Todos os arquivos `.fem`/`.ans`
> de trabalho são salvos em `/tmp/femm_work/` (ASCII puro).

### Rodar todas as configurações

```bash
cd "/home/ribb/Área de trabalho/ufmg/trab_femm"
DISPLAY=:1 ~/femm_env/bin/python main.py
```

Gera automaticamente os CSVs e PNGs de resultados no diretório corrente.

### Gerar figuras de geometria (sem FEMM)

```bash
~/femm_env/bin/python plot_geometry.py
# → motor_geometry_new.png, rotor_geometry_new.png, stator_geometry_new.png
```

### Diagnóstico ferro linear

```bash
DISPLAY=:1 ~/femm_env/bin/python linear_iron_test.py
# → Bg_linear_I.csv, Bg_spectrum_linear_I.png
```

---

## Resultados — Espectro Harmônico (B_g1 = 0,9 T)

| ν | Config I | Config II | Config III | Analítico I/II | Analítico III |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1   | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T | 0,9000 T |
| 5   | 0,0218 T | 0,0218 T | **0,0029 T** | 0,0386 T | 0,0103 T |
| 7   | 0,0125 T | 0,0125 T | **0,0050 T** | 0,0212 T | 0,0057 T |
| 11  | 0,0068 T | 0,0068 T | 0,0067 T | 0,0108 T | 0,0108 T |
| 13  | 0,0060 T | 0,0060 T | 0,0058 T | 0,0091 T | 0,0091 T |
| **23** | **0,2467 T** | **0,2467 T** | **0,2466 T** | — | — |
| **25** | **0,1944 T** | **0,1944 T** | **0,1944 T** | — | — |

**Harmônicos de ranhura do estator:** ν = k·(Q_s/p) ± 1 = k·24 ± 1 → ν = 23, 25, 47, 49.
Independem da configuração de enrolamento e do Q_r.

**Observações:**
- Configs I e II são eletromagneticamente idênticas ✓
- Config III (passo 5/6) atenua ν = 5 em ~87 % e ν = 7 em ~60 % ✓
- Fator de escala *k*_e ≈ 2,0 (Carter + reluctância finita do ferro)
- *B*_g1 bruto (antes da normalização): ≈ 0,45 T

### Diagnóstico ferro linear
Com M250-50A substituído por ferro linear (µ_r = 5 000), os erros em relação ao analítico caem para ≲12 %. O fator *k*_e_lin ≈ 1,88 decompõe-se em: Carter clássico *k*_c,s ≈ 1,42 (abertura de ranhura + entreferro) + reluctância dos dentes preenchidos + modulação do rotor. A saturação do M250-50A é a causa dominante dos desvios (responsável por 25–35 p.p. dos 34–44 p.p. observados).

---

## Decisões de Implementação

| Decisão | Motivo |
|---|---|
| Geometria por linhas radiais + arcos (sem círculo em R_re) | Bug do FEMM: `mi_drawarc` com ângulo pequeno calcula raio errado a partir da corda |
| Config III: circuito único `NC3` com turns = net_AT | Dois block labels na mesma região geram warning e resultado errado |
| Escala pós-hoc *k*_e = B_g1_alvo / B_g1_FEMM | Carter + ferro produzem B ≈ 40 % menor que analítico; escala isola o espectro de forma |
| Rotor Q_r = 52 (não 56) | Dimensões do rotor real disponível no desenho técnico |
| Arquivos `.fem`/`.ans` salvos em `/tmp/femm_work/` | Path `Área de trabalho` contém caractere não-ASCII que o Wine rejeita |

---

## Dependências

| Pacote | Versão testada |
|---|---|
| Python | 3.12 |
| pyFEMM | ≥ 0.0.4 |
| numpy | ≥ 1.26 |
| matplotlib | ≥ 3.8 |
| FEMM | 4.2 (via Wine 9.x) |

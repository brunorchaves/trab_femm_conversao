# Especificação Completa do Motor para Modelagem FEMM
**Projeto FEMM – Conversão da Energia / UFMG | Prof. Braz J. Cardoso Filho**
**Autores: Bruno Ribeiro e Arnaldo**

---

## 1. Parâmetros Gerais da Máquina

| Parâmetro | Símbolo | Valor | Unidade |
|---|---|---|---|
| Número de polos | P | 6 | — |
| Pares de polos | p = P/2 | 3 | — |
| Número de fases | m | 3 | — |
| Ranhuras por polo por fase | q | 4 | — |
| **Ranhuras do estator** | Q_s | **72** | — |
| **Ranhuras do rotor** | Q_r | **28** | — |
| Tensão terminal | V | 127 | V_rms |
| Frequência elétrica | f_e | 60 | Hz |
| Velocidade síncrona n_s = 120·f/P | n_s | 1200 | RPM |
| **Entreferro** | g | **0,50** | mm |
| Comprimento do pacote (profundidade 2D) | L | 140 | mm |
| B máx no núcleo | B_core | 1,7 | T |
| B_g pico (referência analítica) | B_g1 | ≈ 0,9 | T |
| Aço das laminações | — | M250-50A (APERAM E105) | 0,5 mm |
| Material das barras do rotor | — | Alumínio | — |
| Material dos condutores do estator | — | Cobre | — |

### Parâmetros derivados do enrolamento

| Parâmetro | Fórmula | Valor |
|---|---|---|
| Passo polar (ranhuras) | τ_p = Q_s/P | 12 |
| Ângulo elétrico entre ranhuras | α = (P/2)·(360°/Q_s) | 15° |
| Largura do cinturão de fase | q·α | 60° |
| Passo da bobina – passo pleno | y1 = τ_p | 12 ranhuras |
| Passo da bobina – encurtado 5/6 | y1 = (5/6)·τ_p | 10 ranhuras |
| Número de bobinas por fase (camada simples) | Q_s/(2·m) | 12 bobinas |
| Número de bobinas por fase (camada dupla) | Q_s/m | 24 bobinas |

---

## 2. Geometria – Dimensões

### 2.1 Estator

| Dimensão | Símbolo | Valor (mm) | Fonte |
|---|---|---|---|
| Diâmetro externo | D_se | 182,8 | Desenho φ182,8 |
| **Raio externo** | **R_se** | **91,4** | — |
| Diâmetro interno (furo) | D_si | 115,0 | Desenho φ115 |
| **Raio interno (furo)** | **R_si** | **57,5** | — |
| Altura da coroa (yoke) | h_yoke | 15,0 | Desenho "Largura coroa: 15,0 mm" |
| Profundidade total da ranhura | h_s | 18,5 | R_se − R_si − h_yoke = 91,4−57,5−15,4 |
| Passo de ranhura no furo | τ_s = π·D_si/Q_s | 5,02 | calculado |
| **Boca da ranhura (abertura)** | w_so | **1,6** | Detalhe Y |
| Altura da boca (lábio) | h_so | 0,6 | Desenho dim. 0,600 |
| Largura da ranhura (corpo) | w_s_body | ≈ 3,0 | estimado (slot pitch − dente) |
| Raio de fundo da ranhura | R_slot_bot | ≈ 1,25 | Desenho R1,25 |
| Raio de canto do corpo | R_slot_top | ≈ 0,5 | Desenho R0,5 |

**Perfil da ranhura do estator (simplificado para FEMM):**
```
R = 57,5            ──── boca: 1,6 mm ────
R = 58,1  (57,5+0,6) ──── corpo inicia: ~3,0 mm ────
R = 76,0  (57,5+18,5) ─── fundo: ~3,0 mm (levemente trapezoidal) ───
```

> Para a análise harmônica do entreferro (itens c e d), a forma exata
> da ranhura afeta pouco o espectro dos harmônicos principais. O que
> importa é a presença/ausência das aberturas (w_so) e o entreferro g.

### 2.2 Entreferro

| Parâmetro | Valor |
|---|---|
| Espessura total | g = 0,50 mm |
| Raio do furo do estator (face interna) | R_si = 57,50 mm |
| Raio externo do rotor (face externa) | R_re = R_si − g = 57,00 mm |
| Raio médio do entreferro (arco de extração de B_g) | R_ag = 57,25 mm |

### 2.3 Rotor

| Dimensão | Símbolo | Valor (mm) | Fonte |
|---|---|---|---|
| **Raio externo** | **R_re** | **57,0** | R_si − g |
| Diâmetro externo | D_re | 114,0 | — |
| Raio interno (eixo) | R_ri | ≈ 30,0 | estimado (rotor tem 28 barras de ~22 mm deep → folga para eixo) |
| Profundidade da ranhura (útil) | h_r | 19,4 | Desenho dim. 19,400 |
| Profundidade total da ranhura | h_r_total | 22,0 | Desenho dim. 22,000 |
| Largura do topo da barra (face externa) | w_r_top | 6,198 | Desenho |
| Largura do fundo da barra | w_r_bot | 2,031 | Desenho |
| Passo de ranhura no rotor | τ_r = π·D_re/Q_r | 12,78 | calculado |
| Ângulo por ranhura | 360°/Q_r | 12,857° | = 12° 51' 25,7" |

**Perfil da barra do rotor:** trapezoidal
- Topo (a R=57,0 mm): 6,198 mm de largura
- Fundo (a R=57,0−22,0 = 35,0 mm): 2,031 mm de largura
- Barras de alumínio, sem circuito elétrico na simulação magnetostática

---

## 3. Materiais

### 3.1 Laminações – M250-50A (APERAM E105)

Usar a curva B-H da biblioteca do FEMM mais próxima ou inserir os
pontos abaixo (extraídos da Tabela 1 do enunciado):

| H (A/m) | B (T) | Observação |
|---|---|---|
| 0 | 0 | origem |
| 100 | 1,00 | estimado (região linear) |
| 500 | 1,35 | estimado |
| 1000 | 1,52 | estimado |
| 2500 | 1,59 | Tabela 1 |
| 5000 | 1,69 | Tabela 1 |
| 10000 | 1,81 | Tabela 1 |
| 50000 | 2,00 | saturação estimada |

> Na biblioteca do FEMM, o aço mais próximo é **"M-36 Steel"**
> (equivalente ASTM ao M250-50A). Se disponível, usar diretamente.
> Para análise linear (μ_fe → ∞), definir μ_r = 10000 no material.

### 3.2 Barras do rotor – Alumínio

- Condutividade: σ = 3,54 × 10⁷ S/m
- μ_r = 1
- Em análise magnetostática: bloco de alumínio sem circuito atribuído
  (sem corrente induzida — válido para o instante estático)

### 3.3 Condutores do estator – Cobre

- Apenas como blocos de material nas ranhuras
- Cada bloco será atribuído a um circuito de fase (A, B ou C)
- μ_r = 1, σ = 5,8 × 10⁷ S/m (não relevante em magnetostático)

### 3.4 Ar / Vácuo

- Entreferro, slot openings: material "Air"
- μ_r = 1, σ = 0

---

## 4. Configurações de Enrolamento

### Resumo das três configurações

| Config | Camadas | Passo y1 | β = y1/τ_p | k_w1 |
|---|---|---|---|---|
| I | Simples | 12 ranhuras | 1 (pleno) | 0,9577 |
| II | Dupla | 12 ranhuras | 1 (pleno) | 0,9577 |
| III | Dupla | 10 ranhuras | 5/6 (encurtado) | 0,9250 |

**Observação:** Configs I e II têm os mesmos fatores de enrolamento —
a diferença é construtiva (uma vs. duas camadas por ranhura).

### Fatores de enrolamento calculados

| ν | k_d,ν | k_p,ν (β=1) | k_p,ν (β=5/6) | k_w,ν (β=1) | k_w,ν (β=5/6) |
|---|---|---|---|---|---|
| 1 | +0,9577 | +1 | +0,9659 | +0,9577 | +0,9250 |
| 5 | +0,2053 | +1 | +0,2588 | +0,2053 | +0,0531 |
| 7 | −0,1576 | −1 | +0,2588 | +0,1576 | −0,0408 |
| 11 | −0,1261 | −1 | +0,9659 | +0,1261 | −0,1218 |
| 13 | +0,1261 | +1 | −0,9659 | +0,1261 | −0,1218 |

Triplens (ν = 3, 9, 15, …) canceladas na soma trifásica — omitidas.

---

## 5. Atribuição de Ranhuras por Configuração

### 5.1 Convenção de sinais

- **+A** → condutor ligado ao circuito A, sentido positivo (sai do plano)
- **−A** → condutor ligado ao circuito A, sentido negativo (entra no plano)
- Idem para B e C
- Posição angular da ranhura n: θ_n = (n−1) × 5° (mecânicos), com ranhura 1 em θ=0°

### 5.2 Camada superior (todas as configs compartilham)

Padrão que se **repete 3× ao longo das 72 ranhuras** (por período de 24 ranhuras):

| Ranhuras | Camada superior |
|---|---|
| 1–4, 25–28, 49–52 | +A |
| 5–8, 29–32, 53–56 | −C |
| 9–12, 33–36, 57–60 | +B |
| 13–16, 37–40, 61–64 | −A |
| 17–20, 41–44, 65–68 | +C |
| 21–24, 45–48, 69–72 | −B |

### 5.3 Camada inferior – Config II (passo pleno, y1=12)

Regra: `lower(n) = upper(n)` → ambas as camadas têm **a mesma fase e sentido**.

Config II e Config I são eletricamente equivalentes — a diferença é que
Config II tem `2×N_c` condutores por ranhura (N_c por camada) enquanto
Config I tem N_c por ranhura.

### 5.4 Camada inferior – Config III (passo encurtado, y1=10)

Regra: `lower(n) = −upper(n − 10)`, com índices módulo 72.

Tabela completa para um período (ranhuras 1–24), depois repete em 25–48 e 49–72:

| Ranhura | Camada sup. | Camada inf. | Slot "misto"? |
|---|---|---|---|
| 1 | +A | +A | Não |
| 2 | +A | +A | Não |
| 3 | +A | −C | **Sim** |
| 4 | +A | −C | **Sim** |
| 5 | −C | −C | Não |
| 6 | −C | −C | Não |
| 7 | −C | +B | **Sim** |
| 8 | −C | +B | **Sim** |
| 9 | +B | +B | Não |
| 10 | +B | +B | Não |
| 11 | +B | −A | **Sim** |
| 12 | +B | −A | **Sim** |
| 13 | −A | −A | Não |
| 14 | −A | −A | Não |
| 15 | −A | +C | **Sim** |
| 16 | −A | +C | **Sim** |
| 17 | +C | +C | Não |
| 18 | +C | +C | Não |
| 19 | +C | −B | **Sim** |
| 20 | +C | −B | **Sim** |
| 21 | −B | −B | Não |
| 22 | −B | −B | Não |
| 23 | −B | +A | **Sim** |
| 24 | −B | +A | **Sim** |

> Nos 12 slots "mistos" (3,4,7,8,…) as duas camadas pertencem a fases
> diferentes. No FEMM, o slot deve ser dividido em dois blocos
> (camada superior e inferior), cada um atribuído ao seu circuito.

### 5.5 Corrente líquida por ranhura em t=0 (pico da fase A)

Estado de excitação:
```
i_A = I_pk,   i_B = −I_pk/2,   i_C = −I_pk/2
```

Valores em unidades de (N_c × I_pk) por ranhura,
padrão de 24 ranhuras que se repete 3×:

| Ranhura | Config I | Config II | Config III |
|---|---|---|---|
| 1 | +1,0 | +2,0 | +2,0 |
| 2 | +1,0 | +2,0 | +2,0 |
| 3 | +1,0 | +2,0 | +1,5 |
| 4 | +1,0 | +2,0 | +1,5 |
| 5 | +0,5 | +1,0 | +1,0 |
| 6 | +0,5 | +1,0 | +1,0 |
| 7 | +0,5 | +1,0 | 0,0 |
| 8 | +0,5 | +1,0 | 0,0 |
| 9 | −0,5 | −1,0 | −1,0 |
| 10 | −0,5 | −1,0 | −1,0 |
| 11 | −0,5 | −1,0 | −1,5 |
| 12 | −0,5 | −1,0 | −1,5 |
| 13 | −1,0 | −2,0 | −2,0 |
| 14 | −1,0 | −2,0 | −2,0 |
| 15 | −1,0 | −2,0 | −1,5 |
| 16 | −1,0 | −2,0 | −1,5 |
| 17 | −0,5 | −1,0 | −1,0 |
| 18 | −0,5 | −1,0 | −1,0 |
| 19 | −0,5 | −1,0 | 0,0 |
| 20 | −0,5 | −1,0 | 0,0 |
| 21 | +0,5 | +1,0 | +1,0 |
| 22 | +0,5 | +1,0 | +1,0 |
| 23 | +0,5 | +1,0 | +1,5 |
| 24 | +0,5 | +1,0 | +1,5 |

---

## 6. Calibração das Correntes

### Fórmula analítica

Para atingir B_g1 ≈ 0,9 T na fundamental do entreferro:

```
NI_fase = (B_g1 × g × P × π) / (6 × μ_0 × k_w1)
```

Onde NI_fase = N_fase × I_pk (produto ampere-espiras por fase).

| Config | k_w1 | NI_fase (A) |
|---|---|---|
| I e II (β=1) | 0,9577 | ≈ 1175 |
| III (β=5/6) | 0,9250 | ≈ 1216 |

### Escolha de N_c e I_pk

**Config I – camada simples:**
- N_fase = 12 × N_c (12 bobinas em série por fase)
- Recomendado: N_c = 10 espiras/bobina → I_pk ≈ 9,8 A

**Config II – camada dupla passo pleno:**
- N_fase = 24 × N_c (24 bobinas em série por fase)
- Para mesma I_pk que Config I: usar N_c = 5 espiras/camada → I_pk ≈ 9,8 A
  (total de 10 condutores por ranhura = mesma densidade que Config I)

**Config III – camada dupla passo encurtado:**
- N_fase = 24 × N_c, igual à Config II
- I_pk ≈ 9,8 × (1175/1216) ≈ 9,5 A (ligeiramente menor)

### Verificação no FEMM

Após montar cada modelo:
1. Rodar a simulação
2. Extrair B_g(θ) ao longo do arco R_ag = 57,25 mm
3. Calcular FFT → obter B_g1 medido
4. Se B_g1_medido ≠ 0,9 T, escalar as correntes:
   `I_pk_corrigido = I_pk_atual × (0,9 / B_g1_medido)`

---

## 7. Configuração do Modelo FEMM (pyFEMM)

### 7.1 Tipo de problema

```python
femm.newdocument(0)          # 0 = magnetostático
femm.mi_probdef(
    freq    = 0,             # DC / magnetostático
    units   = 'millimeters', # todas as cotas em mm
    type    = 'planar',      # problema 2D planar
    precision = 1e-8,
    depth   = 140,           # comprimento do pacote em mm
    minangle = 30
)
```

### 7.2 Materiais a definir no FEMM

```python
# Aço M250-50A – usar M-36 da biblioteca ou definir pontos B-H
femm.mi_getmaterial('M-36 Steel')        # ou definir custom

# Alumínio (barras do rotor)
femm.mi_addmaterial('Aluminio', 1, 1, 0, 0, 3.54e7, 0, 0, 1, 0, 0, 0, 0, 0)

# Cobre (condutores estator — propriedades magnéticas apenas)
femm.mi_addmaterial('Cobre', 1, 1, 0, 0, 5.8e7, 0, 0, 1, 0, 0, 0, 0, 0)

# Ar
femm.mi_getmaterial('Air')
```

### 7.3 Circuitos de fase

```python
# Para cada configuração, criar 3 circuitos de corrente
# type=1 → fonte de corrente (A)
femm.mi_addcircprop('PhaseA', I_A, 1)   # I_A = I_pk
femm.mi_addcircprop('PhaseB', I_B, 1)   # I_B = -I_pk/2
femm.mi_addcircprop('PhaseC', I_C, 1)   # I_C = -I_pk/2
```

### 7.4 Condição de contorno

```python
# Fronteira externa: A = 0 em raio > estator
# Usar raio externo = 110 mm (≈ 1,2 × R_se = 91,4 mm)
R_boundary = 110  # mm
femm.mi_makeABC(7, 0.0, 0.0, 0.0, R_boundary)
# OU: círculo externo com Dirichlet A=0
```

### 7.5 Geometria – sequência de construção

```
1. Círculo externo (fronteira): R = 110 mm  → material Air, BC = A=0
2. Coroa do estator: anel de R_si+h_s a R_se → material Aço
3. 72 ranhuras do estator:
   - Para cada ranhura n (n=0..71):
     θ_n = n × 5°  (mecânicos, centro da ranhura)
     a) Boca:  retângulo de 1,6 mm × 0,6 mm centrado em R_si
     b) Corpo: trapézio de ~3,0 mm × 18,5 mm de R_si+0,6 a R_si+19,1
4. Dentes do estator: material Aço (região entre ranhuras)
5. Entreferro: anel de R_re a R_si → material Air
6. Coroa do rotor: anel de R_ri+h_r a R_re → material Aço
7. 28 barras do rotor:
   - Para cada barra n (n=0..27):
     θ_n = n × 12,857°
     Trapézio: topo 6,198 mm a R_re, fundo 2,031 mm, profundidade 19,4 mm
8. Núcleo do rotor: anel de R_ri a (R_re−h_r) → material Aço
9. Eixo: círculo R_ri = 30 mm → material Alumínio (ou Air)
```

> Para a construção das ranhuras do estator, usar `mi_drawarc` para os
> arcos e `mi_drawline` para os segmentos retos; depois definir block
> labels no interior de cada região.

### 7.6 Atribuição de rótulos de bloco (block labels)

Para cada ranhura do estator (Config I – camada simples):
```python
# Centroide do bloco no centro geométrico da ranhura
R_label = R_si + 0.6 + h_s / 2   # ≈ 66.85 mm
theta_n  = n * 5.0 * pi/180       # n = 0..71

x_label = R_label * cos(theta_n)
y_label = R_label * sin(theta_n)

# Tabela slot_assignment[n] retorna ('PhaseX', sinal)
circuit, turns_sign = slot_assignment_I(n+1)
femm.mi_addblocklabel(x_label, y_label)
femm.mi_selectlabel(x_label, y_label)
femm.mi_setblockprop('Cobre', 1, 0, circuit, 0, 0, turns_sign * N_c)
femm.mi_clearselected()
```

Para Config III (slots mistos – dois blocos por ranhura):
```python
R_upper = R_si + 0.6 + h_s * 0.25   # ≈ 62.7 mm  (camada superior)
R_lower = R_si + 0.6 + h_s * 0.75   # ≈ 72.4 mm  (camada inferior)
# Atribuir cada bloco ao seu circuito e sinal conforme Seção 5.4
```

---

## 8. Extração de B_g(θ) e FFT

### 8.1 Arco de extração

```python
# Após resolver:  femm.mi_analyze() + femm.mi_loadsolution()
R_ag = 57.25     # raio médio do entreferro (mm)
N_pts = 720      # pontos equiespaçados (resolução 0,5° mecânico)

theta_pts = linspace(0, 2*pi, N_pts, endpoint=False)
Br_vals   = zeros(N_pts)
Bt_vals   = zeros(N_pts)

femm.mo_clearcontour()
for i, th in enumerate(theta_pts):
    x = R_ag * cos(th)
    y = R_ag * sin(th)
    Br_vals[i], Bt_vals[i] = femm.mo_getb(x, y)  # Bx, By → projetar em Br, Bt
    # Br = Bx*cos(th) + By*sin(th)  (componente radial)
```

### 8.2 FFT espacial

```python
from numpy.fft import rfft

# B_g radial ao longo do arco
Bg_radial = Br_vals   # componente radial

# FFT (dupla-face: N_pts pontos → N_pts//2 + 1 coeficientes)
Bg_fft = rfft(Bg_radial) * (2 / N_pts)
freqs  = arange(len(Bg_fft))   # frequência espacial (harmônico mecânico)

# Para uma máquina de P polos, o harmônico ν_eletrico corresponde a
# ν_mecanico = ν_eletrico × (P/2) = ν_eletrico × 3
# Portanto: harmônico fundamental elétrico (ν=1) → ν_mec=3 no FFT

# Converter para harmônicos elétricos:
# B_g1 = |Bg_fft[p]|  onde p = P/2 = 3
```

### 8.3 Harmônicos de ranhura esperados no FFT

| Origem | Fórmula | Valores (M=1,2) |
|---|---|---|
| Ranhuras do estator (Q_s=72, P=6) | ν_s = (2·Q_s·M/P) ± 1 = 24M ± 1 | **ν = 23, 25** (M=1); **47, 49** (M=2) |
| Ranhuras do rotor (Q_r=28, P=6) | ν_r = (2·Q_r·M/P) ± 1 ≈ 9,33M ± 1 | não inteiros para M=1,2 |

> Os harmônicos de ranhura do estator (ν=23, 25) devem aparecer
> claramente no FFT para as três configurações, pois dependem apenas
> da geometria física das 72 ranhuras, não do passo da bobina.

---

## 9. Resultados Analíticos Esperados (referência para validação)

### 9.1 Espectro de B_g (com B_g1 = 0,9 T, μ_ferro → ∞)

| ν | Config I e II (β=1) | Config III (β=5/6) |
|---|---|---|
| 1 | **0,9000 T** | **0,9000 T** |
| 5 | 0,0386 T | 0,0103 T (atenuação ~73%) |
| 7 | 0,0212 T | 0,0057 T (atenuação ~73%) |
| 11 | 0,0108 T | 0,0108 T (inalterado) |
| 13 | 0,0091 T | 0,0091 T (inalterado) |
| 23 | — (ranhura, não predito anal.) | idem |
| 25 | — (ranhura, não predito anal.) | idem |

Relação geral: `|B_g,ν| / |B_g,1| = |k_w,ν| / (ν × |k_w,1|)`

### 9.2 O que o FEMM adiciona em relação à análise analítica

1. **Saturação magnética** – curva B-H não linear do M250-50A distorce a forma de onda
2. **Harmônicos de ranhura** (ν=23,25,47,49…) – surgem da variação de relutância das aberturas de ranhura
3. **Harmônico de ranhura fundamental** esperado em ν=23 ou ν=25 (o de maior amplitude)
4. Comparação direta das amplitudes dos harmônicos de ranhura entre as 3 configurações (devem ser **iguais** entre si, pois dependem da geometria, não do enrolamento)

---

## 10. Variáveis Python – Tabela de Referência Rápida

```python
# ── Geométricas (mm) ──────────────────────────────────────────────
R_se      = 91.4    # raio externo do estator
R_si      = 57.5    # raio interno do estator (furo / bore)
R_re      = 57.0    # raio externo do rotor
R_ri      = 30.0    # raio interno do rotor (eixo) — estimado
R_ag      = 57.25   # raio médio do entreferro
g         = 0.5     # entreferro (mm)
h_s       = 18.5    # profundidade da ranhura do estator
h_yoke_s  = 15.0    # coroa do estator
w_so      = 1.6     # abertura da ranhura (boca)
h_so      = 0.6     # altura da boca
w_s_body  = 3.0     # largura do corpo da ranhura (aprox.)
L_stack   = 140.0   # comprimento do pacote (profundidade 2D)

# ── Máquina ───────────────────────────────────────────────────────
P         = 6       # polos
p         = 3       # pares de polos
m         = 3       # fases
q         = 4       # ranhuras por polo por fase
Q_s       = 72      # ranhuras do estator
Q_r       = 28      # ranhuras do rotor
y1_full   = 12      # passo da bobina – passo pleno (ranhuras)
y1_short  = 10      # passo da bobina – 5/6 encurtado (ranhuras)
alpha_slot = 15.0   # ângulo elétrico entre ranhuras (graus)

# ── Fatores de enrolamento ────────────────────────────────────────
kw1_full  = 0.9577  # β = 1 (Configs I e II)
kw1_short = 0.9250  # β = 5/6 (Config III)

# ── Excitação (t=0, pico da fase A) ──────────────────────────────
Bg1_target = 0.9    # T (fundamental desejada no entreferro)
mu0        = 4 * pi * 1e-7

# NI por fase necessário [A]:
# NI_fase = Bg1_target * (g*1e-3) * P * pi / (6 * mu0 * kw1)
NI_fase_full  = 1175  # A  (para kw1 = 0,9577)
NI_fase_short = 1216  # A  (para kw1 = 0,9250)

# Escolha prática:
N_c   = 10    # espiras por bobina (por camada no caso duplo)
# Config I:  N_fase = 12 * N_c = 120  →  I_pk = NI_fase_full  / 120 ≈ 9,8 A
# Config II: N_fase = 24 * N_c = 240  →  I_pk = NI_fase_full  / 240 ≈ 4,9 A
# Config III: idem Config II mas com NI_fase_short

# Estado de excitação t=0:
I_pk  = NI_fase_full / (12 * N_c)   # para Config I
I_A   = +I_pk
I_B   = -I_pk / 2
I_C   = -I_pk / 2

# ── Pós-processamento ─────────────────────────────────────────────
N_fft_pts    = 720    # pontos ao longo do arco do entreferro
nu_slot_s    = [23, 25, 47, 49]  # harmônicos de ranhura do estator (elétricos)
```

---

## 11. Fluxo de Trabalho para as 3 Configurações

```
Para cada Config em {I, II, III}:
  1. Definir N_c, I_pk conforme Seção 6
  2. Construir geometria completa (Seção 7.5)
  3. Atribuir materiais e circuitos (Seção 7.2–7.6)
  4. Definir contorno externo (Seção 7.4)
  5. Criar malha: femm.mi_createmesh()
  6. Resolver: femm.mi_analyze(1)
  7. Carregar solução: femm.mi_loadsolution()
  8. Extrair B_g(θ) ao longo de R_ag (Seção 8.1)
  9. FFT espacial → espectro de harmônicos (Seção 8.2)
  10. Salvar: B_g_config_X.csv  e  fft_config_X.csv
  11. Plotar: distribuição espacial + espectro em barras
  12. Comparar com Tabela 9.1
```

---

*Documento gerado em 22/05/2026 — use como referência única para implementação do script Python na Etapa 2.*

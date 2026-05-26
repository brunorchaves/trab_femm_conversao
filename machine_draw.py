import matplotlib.pyplot as plt
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# =========================================================
# 1. ESTATOR: 1 Ranhura (Escalonada de 36 para 72)
# =========================================================
# Medidas originais divididas por 2 (aproximadamente)
abertura_est = 2.800 / 2        # Largura da abertura no entreferro = 1.4 mm
largura_topo_est = 5.444 / 2    # Largura da base da cunha = 2.722 mm
raio_fundo_est = 3.885 / 2      # Raio do fundo da gota = 1.942 mm
profundidade_est = 18.5         # Profundidade total mantida

# Construção dos pontos (Simetria no eixo Y)
est_x = [
    -abertura_est/2, -abertura_est/2, 
    -largura_topo_est/2, -largura_topo_est/2, 
    -raio_fundo_est, 0, raio_fundo_est, 
    largura_topo_est/2, largura_topo_est/2, 
    abertura_est/2, abertura_est/2
]

# Alturas correspondentes no eixo Y (0 é o entreferro)
# A gota original tem ponta reta de 0.6mm e angulação de 0.548mm
est_y = [
    0, 0.6, 
    0.6 + 0.548, profundidade_est - raio_fundo_est, 
    profundidade_est, profundidade_est + raio_fundo_est, profundidade_est, 
    profundidade_est - raio_fundo_est, 0.6 + 0.548, 
    0.6, 0
]

ax1.plot(est_x, est_y, 'b-', linewidth=2)
ax1.fill(est_x, est_y, 'blue', alpha=0.1)
ax1.set_title("Estator (1/72) - Perfil Ajustado")
ax1.set_xlabel("Largura (mm)")
ax1.set_ylabel("Profundidade a partir do entreferro (mm)")
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.set_ylim(-2, 22)
ax1.set_xlim(-5, 5)

# =========================================================
# 2. ROTOR: 1 Ranhura (Escalonada de 28 para 56)
# =========================================================
# Medidas originais divididas por 2 (aproximadamente)
abertura_rot = 0.6              # Rasgo do rotor mantido (já é pequeno)
largura_topo_rot = 6.198 / 2    # Largura maior do trapézio = 3.099 mm
largura_fundo_rot = 2.031 / 2   # Largura menor do trapézio = 1.015 mm
profundidade_rot = 22.0         # Profundidade total mantida

# Construção dos pontos (Simetria no eixo Y, invertido para baixo)
rot_x = [
    -abertura_rot/2, -abertura_rot/2,
    -largura_topo_rot/2, -largura_fundo_rot/2,
    largura_fundo_rot/2, largura_topo_rot/2,
    abertura_rot/2, abertura_rot/2
]

# Alturas correspondentes no eixo Y (0 é o entreferro)
rot_y = [
    0, -0.6,
    -0.6 - 1.0, -profundidade_rot,
    -profundidade_rot, -0.6 - 1.0,
    -0.6, 0
]

ax2.plot(rot_x, rot_y, 'darkorange', linewidth=2)
ax2.fill(rot_x, rot_y, 'orange', alpha=0.1)
ax2.set_title("Rotor (1/56) - Perfil Ajustado")
ax2.set_xlabel("Largura (mm)")
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.set_ylim(-24, 2)
ax2.set_xlim(-5, 5)

plt.tight_layout()
plt.show()
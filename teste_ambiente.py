"""
Etapa 1 — Teste de infraestrutura: WINE + FEMM + pyFEMM.
Objetivo: apenas inicializar o FEMM, criar um documento vazio e fechar.
Nenhum código de geometria ou desenho aqui.
"""

import sys
import os
import shutil

# ──────────────────────────────────────────────
# Configuração de caminhos
# ──────────────────────────────────────────────

WINE_PATH  = shutil.which("wine") or "/usr/bin/wine"
# pyFEMM espera o caminho Linux real (não o caminho Windows interno do WINE)
FEMM_LINUX = os.path.expanduser("~/.wine/drive_c/femm42/bin/femm.exe")


# ──────────────────────────────────────────────
# Verificações de pré-requisitos
# ──────────────────────────────────────────────

def verificar_ambiente():
    erros = []

    if not os.path.isfile(WINE_PATH):
        erros.append(
            f"[ERRO] wine não encontrado em '{WINE_PATH}'.\n"
            "  -> Execute: sudo apt install winehq-stable"
        )

    if not os.path.isfile(FEMM_LINUX):
        erros.append(
            f"[ERRO] femm.exe não encontrado em '{FEMM_LINUX}'.\n"
            "  -> Instale o FEMM com: DISPLAY=:1 wine /tmp/femm42_setup.exe /S\n"
            f"  -> Caminho esperado: {FEMM_LINUX}"
        )

    if erros:
        print("\n".join(erros), file=sys.stderr)
        sys.exit(1)

    print(f"[OK] wine encontrado    : {WINE_PATH}")
    print(f"[OK] femm.exe encontrado: {FEMM_LINUX}")


# ──────────────────────────────────────────────
# Teste principal
# ──────────────────────────────────────────────

def main():
    verificar_ambiente()

    try:
        import femm
    except ImportError:
        print(
            "[ERRO] Módulo 'femm' não encontrado.\n"
            "  -> Ative o virtualenv: source ~/femm_env/bin/activate\n"
            "  -> Ou instale: pip install pyfemm",
            file=sys.stderr,
        )
        sys.exit(1)

    print("[OK] pyFEMM importado com sucesso.")

    try:
        print(f"\nAbrindo FEMM via WINE...")
        print(f"  winepath : {WINE_PATH}")
        print(f"  femmpath : {FEMM_LINUX}")

        # femmpath recebe o caminho Linux real do femm.exe (não o caminho Windows)
        femm.openfemm(winepath=WINE_PATH, femmpath=FEMM_LINUX)
        print("[OK] FEMM inicializado.")

    except Exception as e:
        print(
            f"\n[ERRO] Falha ao abrir o FEMM: {e}\n"
            "  Dicas de debug:\n"
            "  1. Teste manualmente: DISPLAY=:1 wine ~/.wine/drive_c/femm42/bin/femm.exe\n"
            "  2. Verifique o display: echo $DISPLAY\n"
            "  3. Reinicie o prefixo: wineboot --init",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        femm.newdocument(0)   # 0 = magnetostático
        print("[OK] Documento magnetostático criado.")

    except Exception as e:
        print(f"[ERRO] Falha ao criar documento: {e}", file=sys.stderr)
        femm.closefemm()
        sys.exit(1)

    finally:
        femm.closefemm()
        print("[OK] FEMM encerrado.\n")

    print("=" * 40)
    print("Ambiente OK — pronto para a Etapa 2.")
    print("=" * 40)


if __name__ == "__main__":
    main()

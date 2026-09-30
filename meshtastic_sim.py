#!/usr/bin/env python3

import time


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# Simula o tempo necessário para o rádio aceitar/transmitir o pacote.
DELAY_TRANSMISSAO = 0.5


# =============================================================================
# INTERFACE MESHTASTIC SIMULADA
# =============================================================================

class MeshtasticSimulador:
    """Simula uma interface Meshtastic para testes do scheduler."""

    def __init__(self):
        print()
        print("Meshtastic Simulator conectado.")

    def sendText(self, mensagem, channelIndex=0):
        """
        Simula o envio de uma mensagem pelo Meshtastic.

        Mantém a mesma chamada utilizada pela API real:
            sendText(mensagem, channelIndex=canal)
        """

        tamanho_bytes = len(
            mensagem.encode("utf-8")
        )

        print()
        print("[SIMULADOR]")
        print(f"Canal: {channelIndex}")
        print(f"Tamanho: {tamanho_bytes} bytes")
        print("Mensagem:")
        print(mensagem)

        time.sleep(DELAY_TRANSMISSAO)

        print("[SIMULADOR] Pacote transmitido.")


    def close(self):
        """Fecha a interface simulada."""

        print()
        print("Meshtastic Simulator desconectado.")


# =============================================================================
# TESTE DIRETO
# =============================================================================

def main():

    print("=" * 80)
    print("MESHTASTIC SIMULATOR")
    print("=" * 80)

    interface = MeshtasticSimulador()

    try:

        interface.sendText(
            "TESTE DO MESHTASTIC",
            channelIndex=2,
        )

    finally:

        interface.close()


if __name__ == "__main__":
    main()

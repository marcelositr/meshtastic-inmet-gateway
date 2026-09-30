#!/usr/bin/env python3

import importlib.util
import time
from datetime import datetime

from meshtastic_sim import MeshtasticSimulador


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# -----------------------------------------------------------------------------
# HORÁRIOS
# -----------------------------------------------------------------------------

HORARIO_ALERTAS = "05:00"

HORARIO_MANHA = "06:00"
HORARIO_TARDE = "12:00"
HORARIO_NOITE = "18:00"


# -----------------------------------------------------------------------------
# CANAIS MESHTASTIC
# -----------------------------------------------------------------------------

CANAL_ALERTAS = 1
CANAL_PREVISAO = 2


# -----------------------------------------------------------------------------
# IDENTIFICAÇÃO DOS CANAIS
# -----------------------------------------------------------------------------

NOME_CANAL_ALERTAS = "ALERTAS INMET"
NOME_CANAL_PREVISAO = "PREVISÃO INMET"


# -----------------------------------------------------------------------------
# TRANSMISSÃO
# -----------------------------------------------------------------------------

DELAY_ENTRE_MENSAGENS = 5


# -----------------------------------------------------------------------------
# TENTATIVAS
# -----------------------------------------------------------------------------

MAX_TENTATIVAS = 2
DELAY_ENTRE_TENTATIVAS = 10


# -----------------------------------------------------------------------------
# MODO DE TESTE
# -----------------------------------------------------------------------------

MODO_TESTE = False


# Valores:
#
#     "alertas"
#     "manha"
#     "tarde"
#     "noite"

BOLETIM_TESTE = "alertas"


# =============================================================================
# MÓDULOS
# =============================================================================

def carregar_modulo(caminho, nome):
    """Carrega um script Python cujo nome pode conter hífens."""

    spec = importlib.util.spec_from_file_location(
        nome,
        caminho,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Não foi possível carregar: {caminho}"
        )

    modulo = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(modulo)

    return modulo


def carregar_modulo_previsao():
    """Carrega o script de previsão do INMET."""

    return carregar_modulo(
        "api-inmet-weatherforecast-v1.py",
        "api_inmet_weatherforecast",
    )


def carregar_modulo_alertas():
    """Carrega o script de alertas do INMET."""

    return carregar_modulo(
        "api-inmet-alert-v1.py",
        "api_inmet_alert",
    )


# =============================================================================
# CONEXÃO MESHTASTIC
# =============================================================================

def conectar_meshtastic():
    """Conecta ao simulador Meshtastic."""

    print()
    print("Conectando ao Meshtastic Simulator...")

    interface = MeshtasticSimulador()

    return interface


def fechar_meshtastic(interface):
    """Fecha a interface Meshtastic."""

    if interface is not None:
        interface.close()


# =============================================================================
# TRANSMISSÃO
# =============================================================================

def enviar_mensagem(interface, mensagem, canal):
    """Envia uma mensagem pelo canal Meshtastic informado."""

    tamanho_bytes = len(
        mensagem.encode("utf-8")
    )

    tamanho_bits = tamanho_bytes * 8

    print()
    print(f"Canal: {canal}")
    print(
        f"Tamanho: "
        f"{tamanho_bytes} bytes | "
        f"{tamanho_bits} bits"
    )
    print("Mensagem:")
    print(mensagem)

    interface.sendText(
        mensagem,
        channelIndex=canal,
    )


def enviar_boletim(
    interface,
    mensagens,
    canal,
    nome_canal,
):
    """Envia todas as mensagens de um boletim."""

    total = len(mensagens)

    print()
    print("=" * 80)
    print(f"ENVIO → {nome_canal}")
    print("=" * 80)
    print(f"Mensagens: {total}")
    print(f"Canal: {canal}")
    print(
        f"Intervalo: "
        f"{DELAY_ENTRE_MENSAGENS}s"
    )

    for numero, mensagem in enumerate(
        mensagens,
        start=1,
    ):

        print()
        print(
            f"[{numero}/{total}] "
            "Enviando mensagem..."
        )

        tentativa = 1

        while tentativa <= MAX_TENTATIVAS:

            try:

                enviar_mensagem(
                    interface,
                    mensagem,
                    canal,
                )

                print(
                    f"[{numero}/{total}] "
                    "Enviada para o rádio."
                )

                break

            except Exception as erro:

                print(
                    f"[{numero}/{total}] "
                    f"Erro na tentativa "
                    f"{tentativa}/{MAX_TENTATIVAS}: "
                    f"{erro}"
                )

                if tentativa >= MAX_TENTATIVAS:

                    print(
                        f"[{numero}/{total}] "
                        "Mensagem descartada após "
                        "atingir o limite de tentativas."
                    )

                    break

                print(
                    f"Aguardando "
                    f"{DELAY_ENTRE_TENTATIVAS}s "
                    "antes de tentar novamente..."
                )

                time.sleep(
                    DELAY_ENTRE_TENTATIVAS
                )

                tentativa += 1

        if numero < total:

            print(
                f"Aguardando "
                f"{DELAY_ENTRE_MENSAGENS}s "
                "antes da próxima mensagem..."
            )

            time.sleep(
                DELAY_ENTRE_MENSAGENS
            )


# =============================================================================
# INMET - PREVISÃO
# =============================================================================

def obter_previsao(tipo):
    """
    Obtém as mensagens da previsão do INMET
    para o período solicitado.
    """

    print()
    print("=" * 80)
    print(
        f"INMET → PREVISÃO "
        f"{tipo.upper()}"
    )
    print("=" * 80)

    try:

        modulo = carregar_modulo_previsao()

        dados = modulo.buscar_previsao()

        municipio = modulo.obter_municipio(
            dados
        )

        if not municipio:
            raise ValueError(
                "Município não encontrado na previsão."
            )

        data, previsao = (
            modulo.obter_previsao_hoje(dados)
        )

        if not previsao:
            raise ValueError(
                "Previsão de hoje não encontrada."
            )

        configuracoes = {
            "manha": (
                "06:00",
                "MANHÃ 🌅",
                "manha",
            ),
            "tarde": (
                "12:00",
                "TARDE 🌇",
                "tarde",
            ),
            "noite": (
                "18:00",
                "NOITE 🌃",
                "noite",
            ),
        }

        configuracao = configuracoes.get(
            tipo
        )

        if not configuracao:
            raise ValueError(
                f"Período inválido: {tipo}"
            )

        horario, nome, chave = configuracao

        print(f"Data: {data}")
        print(f"Horário: {horario}")
        print(f"Período: {nome}")
        print(f"Município: {municipio}")

        mensagens = modulo.criar_boletim(
            data,
            previsao,
            municipio,
            nome,
            chave,
        )

        return mensagens

    except Exception as erro:

        print()
        print(
            f"ERRO AO OBTER PREVISÃO: {erro}"
        )

        return []


# =============================================================================
# INMET - ALERTAS
# =============================================================================

def obter_alertas():
    """Obtém os alertas reais do INMET para o município configurado."""

    print()
    print("=" * 80)
    print("INMET → ALERTAS")
    print("=" * 80)

    try:

        modulo = carregar_modulo_alertas()

        # Consulta a API do INMET.
        dados = modulo.buscar_alertas()

        # Obtém o município pelo código IBGE.
        municipio = modulo.obter_municipio(
            dados
        )

        if not municipio:
            raise ValueError(
                "Município não encontrado nos alertas."
            )

        print(f"Município: {municipio}")

        # Filtra somente os alertas que atingem
        # o município configurado.
        alertas = modulo.filtrar_alertas(
            dados
        )

        print(
            f"Alertas encontrados: "
            f"{len(alertas)}"
        )

        # Mantém o conteúdo da API conforme
        # definido no script de alertas.
        mensagens = modulo.criar_mensagens(
            alertas,
            municipio,
        )

        return mensagens

    except Exception as erro:

        print()
        print(
            f"ERRO AO OBTER ALERTAS: {erro}"
        )

        return []


# =============================================================================
# BOLETINS
# =============================================================================

def obter_boletim(tipo):
    """Obtém as mensagens correspondentes ao boletim."""

    if tipo == "alertas":
        return obter_alertas()

    if tipo in (
        "manha",
        "tarde",
        "noite",
    ):
        return obter_previsao(tipo)

    return []


def obter_configuracao_boletim(tipo):
    """Retorna canal e nome do canal correspondente."""

    if tipo == "alertas":

        return (
            CANAL_ALERTAS,
            NOME_CANAL_ALERTAS,
        )

    return (
        CANAL_PREVISAO,
        NOME_CANAL_PREVISAO,
    )


# =============================================================================
# MODO DE TESTE
# =============================================================================

def executar_teste(interface):
    """Executa imediatamente o boletim configurado."""

    tipo = BOLETIM_TESTE

    canal, nome_canal = (
        obter_configuracao_boletim(tipo)
    )

    mensagens = obter_boletim(tipo)

    if not mensagens:

        print()
        print(
            f"Nenhuma mensagem disponível "
            f"para o teste: {tipo}"
        )

        return

    print()
    print("=" * 80)
    print("MODO DE TESTE")
    print("=" * 80)
    print(f"Boletim: {tipo}")
    print(f"Canal: {nome_canal}")
    print(f"Índice: {canal}")

    enviar_boletim(
        interface,
        mensagens,
        canal,
        nome_canal,
    )


# =============================================================================
# AGENDAMENTO
# =============================================================================

def obter_horario_atual():
    """Retorna o horário atual no formato HH:MM."""

    return datetime.now().strftime("%H:%M")


def verificar_horarios():
    """Verifica se existe algum boletim programado."""

    horario = obter_horario_atual()

    if horario == HORARIO_ALERTAS:
        return "alertas"

    if horario == HORARIO_MANHA:
        return "manha"

    if horario == HORARIO_TARDE:
        return "tarde"

    if horario == HORARIO_NOITE:
        return "noite"

    return None


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():

    print("=" * 80)
    print("MESHTASTIC SCHEDULER")
    print("=" * 80)

    interface = None

    try:

        interface = conectar_meshtastic()

        if MODO_TESTE:

            executar_teste(interface)

            return

        print()
        print("Scheduler iniciado.")
        print()
        print(f"Alertas:  {HORARIO_ALERTAS}")
        print(f"Manhã:    {HORARIO_MANHA}")
        print(f"Tarde:    {HORARIO_TARDE}")
        print(f"Noite:    {HORARIO_NOITE}")

        ultimo_disparo = None

        while True:

            horario = obter_horario_atual()

            tipo = verificar_horarios()

            if (
                tipo
                and horario != ultimo_disparo
            ):

                canal, nome_canal = (
                    obter_configuracao_boletim(
                        tipo
                    )
                )

                mensagens = obter_boletim(
                    tipo
                )

                if mensagens:

                    enviar_boletim(
                        interface,
                        mensagens,
                        canal,
                        nome_canal,
                    )

                ultimo_disparo = horario

            time.sleep(1)

    except KeyboardInterrupt:

        print()
        print(
            "Scheduler interrompido pelo usuário."
        )

    except Exception as erro:

        print()
        print(f"ERRO: {erro}")

    finally:

        fechar_meshtastic(interface)


if __name__ == "__main__":
    main()
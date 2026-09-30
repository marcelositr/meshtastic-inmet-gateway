#!/usr/bin/env python3

import requests
from datetime import datetime


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

BASE_URL = "https://apiprevmet3.inmet.gov.br/previsao"

# Código IBGE do município.
MUNICIPIO_IBGE = "3524105"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) "
        "Gecko/20100101 Firefox/142.0"
    ),
    "Accept": "application/json,text/plain,*/*",
}

TIMEOUT = 30


# =============================================================================
# API
# =============================================================================

def buscar_previsao():
    """Consulta a previsão municipal do INMET."""

    url = f"{BASE_URL}/{MUNICIPIO_IBGE}"

    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    print(f"HTTP: {resposta.status_code}")

    resposta.raise_for_status()

    return resposta.json()


# =============================================================================
# MUNICÍPIO
# =============================================================================

def obter_municipio(dados):
    """Obtém o nome do município retornado pela API."""

    municipio = dados.get(MUNICIPIO_IBGE, {})

    for previsao in municipio.values():
        if not isinstance(previsao, dict):
            continue

        for periodo in previsao.values():
            if not isinstance(periodo, dict):
                continue

            nome = periodo.get("entidade")
            uf = periodo.get("uf")

            if nome and uf:
                return f"{nome} - {uf}"

    return None


# =============================================================================
# FILTRO
# =============================================================================

def obter_previsao_hoje(dados):
    """Retorna somente a previsão do dia atual."""

    hoje = datetime.now().strftime("%d/%m/%Y")

    municipio = dados.get(MUNICIPIO_IBGE, {})
    previsao = municipio.get(hoje, {})

    return hoje, previsao


# =============================================================================
# FORMATAÇÃO
# =============================================================================

def formatar_previsao(nome, dados):
    """Formata o período com as informações principais."""

    resumo = dados.get("resumo", "")

    temp_min = dados.get("temp_min")
    temp_max = dados.get("temp_max")

    umidade_min = dados.get("umidade_min")
    umidade_max = dados.get("umidade_max")

    return "\n".join(
        [
            nome,
            resumo,
            f"Temperatura: {temp_min}°C a {temp_max}°C",
            f"Umidade: {umidade_min}% a {umidade_max}%",
        ]
    )


def formatar_detalhes(dados):
    """Formata vento e tendências de temperatura."""

    direcao_vento = dados.get("dir_vento", "")
    intensidade_vento = dados.get("int_vento", "")

    tendencia_max = dados.get("temp_max_tende", "")
    tendencia_min = dados.get("temp_min_tende", "")

    return "\n".join(
        [
            f"Vento: {direcao_vento}, {intensidade_vento}",
            f"Tendência máxima: {tendencia_max}",
            f"Tendência mínima: {tendencia_min}",
        ]
    )


def criar_boletim(data, previsao, municipio, nome, chave):
    """
    Cria um boletim independente para um período.

    Cada boletim possui exatamente três mensagens:
    1. Cabeçalho
    2. Previsão
    3. Detalhes
    """

    dados_periodo = previsao.get(chave)

    if not dados_periodo:
        return []

    mensagens = []

    cabecalho = (
        f"📆 {data} - INMET - {municipio.upper()}"
    )

    if chave == "manha":
        nascer = dados_periodo.get("nascer", "")
        ocaso = dados_periodo.get("ocaso", "")

        cabecalho += (
            f"\nNascer: {nascer} | Ocaso: {ocaso}"
        )

    mensagens.append(cabecalho)

    mensagens.append(
        formatar_previsao(
            nome,
            dados_periodo,
        )
    )

    mensagens.append(
        formatar_detalhes(
            dados_periodo,
        )
    )

    return mensagens


# =============================================================================
# SAÍDA
# =============================================================================

def mostrar_boletim(horario, mensagens):
    """Exibe um boletim independente."""

    if not mensagens:
        return

    total = len(mensagens)

    print()
    print("#" * 80)
    print(f"BOLETIM {horario}")
    print("#" * 80)

    for numero, mensagem in enumerate(mensagens, start=1):
        tamanho_bytes = len(
            mensagem.encode("utf-8")
        )

        tamanho_bits = tamanho_bytes * 8

        print()
        print("=" * 80)
        print(f"MENSAGEM {numero}/{total}")
        print("=" * 80)
        print(mensagem)
        print()
        print(
            f"[{tamanho_bytes} bytes | "
            f"{tamanho_bits} bits]"
        )


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    print("=" * 80)
    print("INMET → PREVISÃO DO TEMPO")
    print("=" * 80)

    try:
        dados = buscar_previsao()

        municipio = obter_municipio(dados)

        if not municipio:
            print(
                f"\nMunicípio com código IBGE "
                f"{MUNICIPIO_IBGE} não encontrado."
            )
            return

        print(f"Município: {municipio}")

        data, previsao = obter_previsao_hoje(dados)

        periodos = (
            ("06:00", "MANHÃ 🌅", "manha"),
            ("12:00", "TARDE 🌇", "tarde"),
            ("18:00", "NOITE 🌃", "noite"),
        )

        for horario, nome, chave in periodos:
            mensagens = criar_boletim(
                data,
                previsao,
                municipio,
                nome,
                chave,
            )

            mostrar_boletim(
                horario,
                mensagens,
            )

    except requests.RequestException as erro:
        print(f"\nERRO HTTP: {erro}")

    except Exception as erro:
        print(f"\nERRO: {erro}")


if __name__ == "__main__":
    main()

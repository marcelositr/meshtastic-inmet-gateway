# Meshtastic INMET Gateway

Gateway de automação para [Meshtastic](https://meshtastic.org/) que consulta dados meteorológicos do [INMET](https://www.gov.br/inmet/) e transmite alertas e previsões pela rede LoRa.

O projeto foi desenvolvido inicialmente para operação em **Ituverava, São Paulo, Brasil**, utilizando o código IBGE do município para selecionar os dados meteorológicos correspondentes.

## Arquitetura

```text
                    INTERNET
                       │
                       ▼
                  ┌─────────┐
                  │  INMET  │
                  └────┬────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Python Scheduler│
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Meshtastic   │
              └────────┬────────┘
                       │
                      LoRa
                       │
                       ▼
                  REDE MESH
```

### Arquitetura planejada

A integração final deverá utilizar um hotspot Linux como servidor da automação e uma Heltec LoRa 32 V4 como rádio Meshtastic.

```text
                    INTERNET
                       │
                       ▼
              ┌─────────────────┐
              │   Hotspot DMR   │
              │    Linux/RPi    │
              │                 │
              │ Python          │
              │ Scheduler       │
              │ INMET           │
              └────────┬────────┘
                       │
                      Wi-Fi
                       │
                       ▼
              ┌─────────────────┐
              │   Heltec V4     │
              │   Meshtastic    │
              └────────┬────────┘
                       │
                      LoRa
                       │
                       ▼
                  REDE MESH
```

A comunicação entre o hotspot e a Heltec deverá utilizar Wi-Fi, eliminando a necessidade de uma conexão USB permanente entre os equipamentos.

## Funcionalidades

* Consulta à API oficial do INMET.
* Identificação do município através do código IBGE.
* Consulta de alertas meteorológicos ativos.
* Consulta da previsão meteorológica.
* Separação da previsão em:

  * Manhã
  * Tarde
  * Noite
* Transmissão através de canais Meshtastic distintos.
* Intervalo configurável entre mensagens.
* Sistema de tentativas de transmissão.
* Scheduler automático.
* Simulador Meshtastic para desenvolvimento sem o hardware.
* Exibição do tamanho das mensagens em bytes e bits para testes.

## Agendamento

O scheduler foi projetado para transmitir:

| Horário | Conteúdo          | Canal |
| ------- | ----------------- | ----: |
| 05:00   | Alertas INMET     |     1 |
| 06:00   | Previsão da manhã |     2 |
| 12:00   | Previsão da tarde |     2 |
| 18:00   | Previsão da noite |     2 |

Os horários podem ser alterados na configuração do scheduler.

## Organização

```text
meshtastic-inmet-gateway/
│
├── api-inmet-alert-v1.py
├── api-inmet-weatherforecast-v1.py
├── meshtastic-scheduler.py
├── meshtastic_sim.py
├── README.md
└── LICENSE
```

### `api-inmet-alert-v1.py`

Responsável por consultar os alertas do INMET, localizar o município configurado e transformar os dados recebidos em mensagens individuais.

O conteúdo meteorológico retornado pela API não é reinterpretado pelo programa. Os campos fornecidos pelo INMET são apenas separados em mensagens menores para transmissão.

### `api-inmet-weatherforecast-v1.py`

Responsável por consultar a previsão do INMET e gerar os boletins correspondentes aos períodos da manhã, tarde e noite.

### `meshtastic-scheduler.py`

Responsável pelo agendamento e transmissão dos boletins.

### `meshtastic_sim.py`

Simulador utilizado durante o desenvolvimento para testar a comunicação do scheduler sem a presença do rádio Meshtastic físico.

## Configuração

As principais configurações ficam no início dos arquivos para facilitar a adaptação do projeto.

Exemplo:

```python
MUNICIPIO_IBGE = "3524105"
```

O código `3524105` corresponde a Ituverava, SP.

Os canais e horários do scheduler também podem ser configurados diretamente no arquivo:

```python
HORARIO_ALERTAS = "05:00"

HORARIO_MANHA = "06:00"
HORARIO_TARDE = "12:00"
HORARIO_NOITE = "18:00"

CANAL_ALERTAS = 1
CANAL_PREVISAO = 2
```

## Dependências

O projeto utiliza Python 3 e as bibliotecas necessárias para consulta à API e comunicação com Meshtastic.

Instalação da biblioteca Meshtastic:

```bash
python3 -m pip install meshtastic
```

A comunicação com o hardware Meshtastic será integrada posteriormente.

## Desenvolvimento sem hardware

Enquanto o rádio não estiver disponível, o projeto pode utilizar o simulador:

```bash
python3 meshtastic_sim.py
```

O scheduler também pode ser executado em modo de teste:

```python
MODO_TESTE = True
```

Nesse modo, o boletim definido em:

```python
BOLETIM_TESTE = "alertas"
```

é executado imediatamente.

Para testar outros boletins:

```python
BOLETIM_TESTE = "manha"
```

ou:

```python
BOLETIM_TESTE = "tarde"
```

ou:

```python
BOLETIM_TESTE = "noite"
```

Quando o modo de teste estiver desativado:

```python
MODO_TESTE = False
```

o scheduler passa a aguardar os horários configurados.

## Mensagens

Os boletins são divididos em mensagens independentes para transmissão pela rede Meshtastic.

Exemplo:

```text
📆 30/09/2026 - INMET - ITUVERAVA - SP
```

```text
TARDE 🌇
Muitas nuvens com pancadas de chuva e trovoadas isoladas
Temperatura: 25°C a 38°C
Umidade: 20% a 60%
```

```text
Vento: SW-NW, Fracos
Tendência máxima: Estável
Tendência mínima: Estável
```

O programa calcula o tamanho de cada mensagem em UTF-8 para auxiliar nos testes de transmissão.

## Princípios do projeto

O projeto procura manter uma arquitetura simples e previsível:

* Utilizar diretamente os dados fornecidos pelo INMET.
* Evitar reescrever ou reinterpretar textos meteorológicos.
* Manter as APIs separadas do scheduler.
* Manter a camada de comunicação Meshtastic separada da lógica meteorológica.
* Evitar dependências desnecessárias.
* Facilitar manutenção e reutilização.
* Desenvolver e testar sem depender do hardware físico.

## Status

**Em desenvolvimento.**

### Concluído

* [x] Integração com API de alertas do INMET
* [x] Identificação por código IBGE
* [x] Integração com previsão do INMET
* [x] Separação manhã/tarde/noite
* [x] Scheduler
* [x] Canais Meshtastic separados
* [x] Sistema de tentativas
* [x] Simulador Meshtastic
* [x] Testes de transmissão simulada

### Próximas etapas

* [ ] Receber e configurar a Heltec LoRa 32 V4
* [ ] Configurar Meshtastic no hardware
* [ ] Testar comunicação Wi-Fi
* [ ] Substituir o simulador pela interface Meshtastic real
* [ ] Testar transmissão física via LoRa
* [ ] Instalar o scheduler no hotspot Linux
* [ ] Configurar inicialização automática no boot
* [ ] Testar operação contínua

## INMET

Os dados meteorológicos utilizados pelo projeto são fornecidos pelo Instituto Nacional de Meteorologia (INMET).

O projeto não é afiliado ao INMET.

## Licença

Este projeto é distribuído sob a licença **MIT**.

Consulte o arquivo [`LICENSE`](LICENSE) para os termos completos.

---

**Projeto:** `meshtastic-inmet-gateway`

**Autor:** Marcelo Trindade - PU2OMT

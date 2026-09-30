# Meshtastic INMET Gateway

Gateway de automação para [Meshtastic](https://meshtastic.org/) que consulta dados meteorológicos do [Instituto Nacional de Meteorologia (INMET)](https://www.gov.br/inmet/) e distribui alertas e previsões por uma rede Meshtastic utilizando LoRa.

O projeto foi desenvolvido inicialmente para **Ituverava, São Paulo, Brasil**, utilizando o código IBGE do município para identificar os dados meteorológicos correspondentes.

## Visão geral

O gateway foi projetado para operar de forma autônoma. Um host Linux consulta os dados do INMET, executa o agendamento dos boletins e encaminha as mensagens para um nó Meshtastic responsável pela transmissão na rede LoRa.

### Arquitetura atual de desenvolvimento

```text
┌──────────────┐
│    INMET     │
│  APIs Web    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Gateway Python       │
│                      │
│ Integração com API   │
│ Scheduler            │
│ Preparação mensagens │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Interface Meshtastic │
└──────────┬───────────┘
           │
          LoRa
           │
           ▼
      Rede Meshtastic
```

### Arquitetura de implantação prevista

A implantação final está planejada para utilizar um hotspot Linux de operação contínua e uma **Heltec LoRa 32 V4** executando Meshtastic.

```text
                    Internet
                       │
                       ▼
┌─────────────────────────────────┐
│ Hotspot Linux                    │
│                                 │
│ Gateway Python                  │
│ Scheduler                       │
│ Integração INMET                │
└───────────────┬─────────────────┘
                │
              Wi-Fi
                │
                ▼
┌─────────────────────────────────┐
│ Heltec LoRa 32 V4               │
│ Meshtastic                      │
└───────────────┬─────────────────┘
                │
               LoRa
                │
                ▼
         Rede Meshtastic
```

A comunicação planejada por Wi-Fi elimina a necessidade de uma conexão USB permanente entre o host Linux e o rádio Meshtastic.

## Funcionalidades

- Integração com as APIs oficiais do INMET.
- Identificação do município por código IBGE.
- Consulta de alertas meteorológicos ativos.
- Consulta da previsão meteorológica.
- Boletins independentes para manhã, tarde e noite.
- Separação dos dados em mensagens individuais para transmissão.
- Canais Meshtastic distintos para alertas e previsões.
- Intervalo configurável entre mensagens.
- Sistema configurável de tentativas de transmissão.
- Agendamento automático.
- Operação sem intervenção durante o funcionamento normal.
- Simulador Meshtastic para desenvolvimento sem hardware.
- Exibição do tamanho das mensagens em bytes e bits.

## Agendamento

A configuração padrão do scheduler é:

| Horário | Conteúdo | Canal |
|--------:|----------|------:|
| 05:00 | Alertas INMET | 1 |
| 06:00 | Previsão da manhã | 2 |
| 12:00 | Previsão da tarde | 2 |
| 18:00 | Previsão da noite | 2 |

Os horários e índices dos canais podem ser alterados diretamente na configuração do scheduler.

## Estrutura do projeto

```text
meshtastic-inmet-gateway/
├── api-inmet-alert-v1.py
├── api-inmet-weatherforecast-v1.py
├── meshtastic-scheduler.py
├── meshtastic_sim.py
├── .gitignore
├── LICENSE
└── README.md
```

### Componentes

#### `api-inmet-alert-v1.py`

Consulta os alertas ativos do INMET, identifica o município configurado, filtra os alertas aplicáveis e separa os campos da API em mensagens menores.

O conteúdo meteorológico retornado pelo INMET não é reescrito ou reinterpretado pelo gateway.

#### `api-inmet-weatherforecast-v1.py`

Consulta a previsão do INMET para o município configurado e gera boletins independentes para os períodos da manhã, tarde e noite.

#### `meshtastic-scheduler.py`

Coordena a operação do gateway, incluindo o agendamento, obtenção dos boletins, transmissão das mensagens, tratamento de tentativas e seleção dos canais Meshtastic.

#### `meshtastic_sim.py`

Fornece uma interface Meshtastic simulada para desenvolvimento e testes sem a presença do hardware físico.

## Configuração

O município é selecionado por meio do código IBGE:

```python
MUNICIPIO_IBGE = "3524105"
```

O código `3524105` corresponde a Ituverava, São Paulo.

A configuração dos horários e canais do scheduler é feita diretamente no arquivo:

```python
HORARIO_ALERTAS = "05:00"

HORARIO_MANHA = "06:00"
HORARIO_TARDE = "12:00"
HORARIO_NOITE = "18:00"

CANAL_ALERTAS = 1
CANAL_PREVISAO = 2
```

Os parâmetros de transmissão também podem ser ajustados no scheduler.

## Requisitos

- Python 3
- Acesso à Internet para consultas às APIs do INMET
- Biblioteca Python do Meshtastic para integração com o hardware

Instalação da biblioteca Meshtastic:

```bash
python3 -m pip install meshtastic
```

Durante o desenvolvimento, o projeto pode ser executado e testado sem hardware Meshtastic físico.

## Desenvolvimento e testes

### Simulador Meshtastic

Execute o simulador diretamente:

```bash
python3 meshtastic_sim.py
```

### Modo de teste do scheduler

O scheduler pode executar imediatamente um boletim específico, sem aguardar o horário programado:

```python
MODO_TESTE = True
BOLETIM_TESTE = "alertas"
```

Boletins disponíveis para teste:

```text
alertas
manha
tarde
noite
```

Para operação agendada:

```python
MODO_TESTE = False
```

Nesse modo, o scheduler aguarda os horários configurados.

## Formato das mensagens

Os boletins de previsão são divididos em mensagens independentes para manter as transmissões compactas.

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

O tamanho de cada mensagem é calculado utilizando codificação UTF-8 para auxiliar na análise das transmissões durante o desenvolvimento.

## Princípios de projeto

O projeto utiliza uma arquitetura deliberadamente simples e orientada à manutenção:

1. **Utilizar dados oficiais do INMET**, evitando interpretações desnecessárias.
2. **Separar responsabilidades** entre integração com as APIs, agendamento e transporte Meshtastic.
3. **Manter a configuração explícita** e fácil de adaptar.
4. **Minimizar dependências** e complexidade operacional.
5. **Permitir desenvolvimento sem hardware** por meio de simulação.
6. **Manter o gateway reutilizável** para outros municípios e implantações.

## Status do projeto

**Em desenvolvimento.**

### Concluído

- [x] Integração com a API de alertas do INMET
- [x] Identificação do município por código IBGE
- [x] Integração com a API de previsão do INMET
- [x] Boletins para manhã, tarde e noite
- [x] Execução agendada dos boletins
- [x] Canais Meshtastic separados
- [x] Sistema de tentativas de transmissão
- [x] Simulador Meshtastic
- [x] Testes de transmissão simulada

### Próximas etapas

- [ ] Configurar a Heltec LoRa 32 V4
- [ ] Configurar o Meshtastic no hardware
- [ ] Estabelecer a comunicação Wi-Fi com o host do gateway
- [ ] Substituir o simulador pela interface Meshtastic real
- [ ] Validar a transmissão física via LoRa
- [ ] Implantar o gateway no hotspot Linux
- [ ] Configurar inicialização automática
- [ ] Validar operação contínua e autônoma

## Fonte dos dados

Os dados meteorológicos utilizados pelo projeto são fornecidos pelo **Instituto Nacional de Meteorologia (INMET)**.

O projeto é independente e não possui vínculo institucional com o INMET.

## Licença

Este projeto é distribuído sob a [Licença MIT](LICENSE).

## Autor

**Marcelo Trindade - PU2OMT**

Repositório: [meshtastic-inmet-gateway](https://github.com/marcelositr/meshtastic-inmet-gateway)

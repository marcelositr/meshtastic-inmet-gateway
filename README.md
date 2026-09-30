# Meshtastic INMET Gateway

Automated gateway for [Meshtastic](https://meshtastic.org/) that retrieves meteorological data from the [Brazilian National Institute of Meteorology (INMET)](https://www.gov.br/inmet/) and distributes alerts and forecasts through a Meshtastic LoRa network.

The project is initially configured for **Ituverava, São Paulo, Brazil**, using the municipality's IBGE code to identify the corresponding meteorological data.

## Overview

The gateway is designed to operate as an unattended service. A Linux host retrieves data from INMET, schedules the bulletins, and forwards them to a Meshtastic node for transmission over the LoRa mesh.

### Current development architecture

```text
┌──────────────┐
│    INMET     │
│  Web APIs    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Python Gateway       │
│                      │
│ API integration      │
│ Scheduler            │
│ Message preparation  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Meshtastic Interface │
└──────────┬───────────┘
           │
          LoRa
           │
           ▼
     Meshtastic Mesh
```

### Target deployment architecture

The production deployment is planned around an always-on Linux hotspot and a **Heltec LoRa 32 V4** running Meshtastic.

```text
                    Internet
                       │
                       ▼
┌─────────────────────────────────┐
│ Linux Hotspot                    │
│                                 │
│ Python Gateway                  │
│ Scheduler                       │
│ INMET API integration           │
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
          Meshtastic Mesh
```

The planned Wi-Fi connection removes the need for a permanent USB connection between the Linux host and the Meshtastic radio.

## Features

- Integration with the official INMET APIs.
- Municipality selection using the IBGE code.
- Active meteorological alert retrieval.
- Daily weather forecast retrieval.
- Forecast bulletins for morning, afternoon, and night.
- Independent messages for Meshtastic transmission.
- Separate Meshtastic channels for alerts and forecasts.
- Configurable transmission interval.
- Configurable transmission retry mechanism.
- Scheduled unattended operation.
- Hardware-independent development through a Meshtastic simulator.
- UTF-8 message size reporting in bytes and bits.

## Schedule

The default scheduler configuration is:

| Time | Bulletin | Channel |
|------|----------|--------:|
| 05:00 | INMET alerts | 1 |
| 06:00 | Morning forecast | 2 |
| 12:00 | Afternoon forecast | 2 |
| 18:00 | Night forecast | 2 |

All schedule times and channel indexes are configurable.

## Project Structure

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

### Components

#### `api-inmet-alert-v1.py`

Retrieves active INMET alerts, identifies the configured municipality, filters applicable alerts, and separates the API fields into smaller messages.

Meteorological content returned by INMET is not rewritten or interpreted by the gateway.

#### `api-inmet-weatherforecast-v1.py`

Retrieves the INMET forecast for the configured municipality and generates independent bulletins for the morning, afternoon, and night periods.

#### `meshtastic-scheduler.py`

Coordinates the gateway operation, including schedule management, bulletin retrieval, message transmission, retry handling, and Meshtastic channel selection.

#### `meshtastic_sim.py`

Provides a lightweight Meshtastic interface simulator for development and testing without physical radio hardware.

## Configuration

The municipality is selected through its IBGE code:

```python
MUNICIPIO_IBGE = "3524105"
```

The code `3524105` corresponds to Ituverava, São Paulo.

Scheduler configuration:

```python
HORARIO_ALERTAS = "05:00"

HORARIO_MANHA = "06:00"
HORARIO_TARDE = "12:00"
HORARIO_NOITE = "18:00"

CANAL_ALERTAS = 1
CANAL_PREVISAO = 2
```

Transmission parameters are also configurable in the scheduler.

## Requirements

- Python 3
- Internet access for INMET API requests
- Meshtastic Python library for hardware integration

Install the Meshtastic Python library with:

```bash
python3 -m pip install meshtastic
```

The project is currently developed and tested without requiring physical Meshtastic hardware.

## Development and Testing

### Meshtastic simulator

Run the simulator directly:

```bash
python3 meshtastic_sim.py
```

### Scheduler test mode

The scheduler can execute a bulletin immediately without waiting for its scheduled time:

```python
MODO_TESTE = True
BOLETIM_TESTE = "alertas"
```

Available test bulletins:

```text
alertas
manha
tarde
noite
```

For scheduled operation:

```python
MODO_TESTE = False
```

The scheduler then waits for the configured times.

## Message Format

Forecast bulletins are divided into independent messages to keep individual transmissions compact.

Example:

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

Message size is calculated using UTF-8 encoding to support transmission analysis during development.

## Design Principles

The project follows a deliberately simple and maintainable architecture:

1. **Use official INMET data** without unnecessary reinterpretation.
2. **Separate responsibilities** between API integration, scheduling, and Meshtastic transport.
3. **Keep configuration explicit** and easy to adapt.
4. **Minimize dependencies** and operational complexity.
5. **Support development without hardware** through simulation.
6. **Keep the gateway reusable** for other municipalities and deployments.

## Project Status

**Development in progress.**

### Completed

- [x] INMET active alert API integration
- [x] Municipality identification by IBGE code
- [x] INMET forecast API integration
- [x] Morning, afternoon, and night forecast bulletins
- [x] Scheduled bulletin execution
- [x] Separate Meshtastic channels
- [x] Transmission retry handling
- [x] Meshtastic simulator
- [x] Simulated transmission tests

### Next Steps

- [ ] Configure the Heltec LoRa 32 V4
- [ ] Configure Meshtastic on the hardware
- [ ] Establish Wi-Fi communication with the gateway host
- [ ] Replace the simulator with the real Meshtastic interface
- [ ] Validate physical LoRa transmission
- [ ] Deploy the gateway on the Linux hotspot
- [ ] Configure automatic startup
- [ ] Validate continuous unattended operation

## Data Source

Meteorological data is provided by the **Instituto Nacional de Meteorologia (INMET)**.

This project is independent and is not affiliated with INMET.

## License

This project is licensed under the [MIT License](LICENSE).

## Author

**Marcelo Trindade - PU2OMT**

Repository: [meshtastic-inmet-gateway](https://github.com/marcelositr/meshtastic-inmet-gateway)

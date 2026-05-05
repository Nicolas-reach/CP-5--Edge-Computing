# CP5-Edge -- 🍷 IoT Vinheria Agnello - Sistema de Monitoramento Inteligente

## 📖 Objetivo do Projeto
O **IoT Vinheria Agnello** é um sistema de monitoramento ambiental desenvolvido para garantir a qualidade no armazenamento de vinhos. Vinhos são produtos extremamente sensíveis a variações de temperatura, umidade e exposição à luz. 

Este projeto utiliza um microcontrolador ESP32 para coletar dados em tempo real do ambiente e enviá-los para uma arquitetura robusta baseada em **FIWARE** na nuvem/servidor local. Em caso de anomalias (temperatura alta/baixa, ambiente seco ou excesso de luz), o sistema dispara alertas sonoros e visuais no local, além de registrar todo o histórico em um Dashboard web para análise do administrador.

---

## 🛠️ Tecnologias Utilizadas

### Hardware
* **Microcontrolador:** ESP32 Dev Module
* **Sensores:** DHT11 (Temperatura e Umidade) e LDR (Luminosidade)
* **Atuadores:** Buzzer Ativo (Alarme sonoro) e LED (Alerta visual)

### Software & Backend
* **Linguagens:** C++ (Firmware Arduino), Python (Dashboard)
* **Comunicação:** Protocolo MQTT (HiveMQ Public Broker)
* **Plataforma IoT (FIWARE):**
  * **Orion Context Broker:** Gerenciamento de contexto em tempo real.
  * **IoT Agent UltraLight:** Tradução de mensagens MQTT para NGSI.
  * **STH-Comet:** Armazenamento de dados históricos.
  * **MongoDB:** Banco de dados NoSQL.
* **Infraestrutura:** Docker & Docker Compose
* **Frontend:** Python Flask, HTML, CSS, JS (Gráficos)

---

## 🔌 Esquema de Ligação (Hardware)
Caso vá montar o circuito físico, siga a pinagem abaixo:
* **DHT11 (Sinal):** Pino Digital `4`
* **LDR (Sinal Analógico):** Pino Analógico `34`
* **Buzzer (Positivo):** Pino Digital `18`
* **LED (Positivo):** Pino Digital `2`

---

## 🚀 Como Rodar o Projeto na Sua Máquina

### Pré-requisitos
Antes de começar, você precisará ter instalado em sua máquina:
1. [Arduino IDE](https://www.arduino.cc/en/software) (com as bibliotecas `WiFi`, `PubSubClient` e `DHT sensor library`).
2. [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/).
3. [Python 3.x](https://www.python.org/) (com a biblioteca `Flask` e `requests`).

### Passo 1: Configurar e Ligar o ESP32
1. Abra o arquivo `.ino` na Arduino IDE.
2. Altere as variáveis `ssid` e `password` para o nome e senha da sua rede Wi-Fi.
   > ⚠️ **Atenção:** Evite usar redes corporativas ou de faculdades, pois elas costumam bloquear a porta `1883` (MQTT). Prefira rotear a internet do seu celular ou usar o Wi-Fi de casa.
3. Conecte o ESP32 ao computador e faça o **Upload** do código.

### Passo 2: Subir a Arquitetura FIWARE (Backend)
1. Abra o terminal e navegue até a pasta onde está o seu arquivo `docker-compose.yml`.
2. Execute o comando para baixar e iniciar todos os contêineres em segundo plano:
   ```bash
   sudo docker-compose up -d
   ```

    Aguarde cerca de 15 segundos para que todos os serviços (Orion, STH, IoT Agent e Mongo) estejam completamente iniciados.

Passo 3: Provisionamento (Cadastrar o Dispositivo)

Para que o FIWARE reconheça o ESP32 e grave o histórico, é necessário injetar as configurações no banco de dados. No terminal, execute os 3 comandos abaixo em sequência (você deve receber um retorno 201 Created para cada um):

1. Criar o Serviço IoT:
Bash
```
curl -iX POST '[http://127.0.0.1:4041/iot/services](http://127.0.0.1:4041/iot/services)' \
-H 'fiware-service: smart' \
-H 'fiware-servicepath: /' \
-H 'Content-Type: application/json' \
-d '{"services": [{"apikey": "vinheria_key", "cbroker": "http://orion:1026", "entity_type": "Vinheria", "resource": "/iot/d"}]}'
```
2. Cadastrar o ESP32:
Bash
```
curl -iX POST '[http://127.0.0.1:4041/iot/devices](http://127.0.0.1:4041/iot/devices)' \
-H 'fiware-service: smart' \
-H 'fiware-servicepath: /' \
-H 'Content-Type: application/json' \
-d '{"devices": [{"device_id": "esp32_001", "entity_name": "urn:ngsi-ld:Vinheria:001", "entity_type": "Vinheria", "protocol": "PDI-IoTA-UltraLight", "transport": "MQTT", "attributes": [{"object_id": "t", "name": "temperature", "type": "Float"}, {"object_id": "h", "name": "humidity", "type": "Float"}, {"object_id": "l", "name": "luminosity", "type": "Integer"}]}]}'
```
3. Criar Inscrição no STH-Comet (Histórico):
Bash
```
curl -iX POST '[http://127.0.0.1:1026/v2/subscriptions](http://127.0.0.1:1026/v2/subscriptions)' \
-H 'fiware-service: smart' \
-H 'fiware-servicepath: /' \
-H 'Content-Type: application/json' \
-d '{"description": "Notificar STH", "subject": {"entities": [{"id": "urn:ngsi-ld:Vinheria:001", "type": "Vinheria"}], "condition": {"attrs": ["temperature", "humidity", "luminosity"]}}, "notification": {"http": {"url": "http://sth-comet:8666/notify"}, "attrs": ["temperature", "humidity", "luminosity"], "attrsFormat": "legacy"}}'
```
Nota: Se o Docker não estiver recebendo os dados do broker público, reinicie o agente de IoT:
Bash

sudo docker-compose restart iot-agent

Passo 4: Rodar o Dashboard de Monitoramento

    Navegue até a pasta do seu painel Python (dashboard).

    Instale as dependências caso ainda não tenha feito:
    Bash

    pip install flask requests

3. Inicie o servidor web local:
   ```bash
   python dashboard.py
   ```

    Abra o seu navegador e acesse: http://127.0.0.1:5001

Se os dados estiverem saindo do seu ESP32, você verá as linhas dos gráficos de Temperatura, Umidade e Luminosidade atualizando no painel em tempo real.

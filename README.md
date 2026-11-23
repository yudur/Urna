# Urna — Sistema de Votação Eletrônica de Turma

Projeto acadêmico para **Redes de Computadores I**. Clientes em terminais distintos enviam votos a um servidor central por conexões TCP diretas. Não são utilizados HTTP, REST ou frameworks web.

## Objetivos acadêmicos

- Aplicar o modelo cliente-servidor.
- Usar sockets TCP, `bind()`, `listen()`, `accept()`, `connect()`, `sendall()` e `recv()`.
- Praticar concorrência com threads e sincronização com `threading.Lock`.
- Validar mensagens e prevenir votação duplicada.
- Demonstrar o sistema em máquinas virtuais Debian.

## Tecnologias

- Python 3 e biblioteca padrão.
- Sockets TCP IPv4.
- Threads do módulo `threading`.
- JSON delimitado por newline.
- Debian Linux e VirtualBox.

## Início rápido

Na máquina que será o servidor, abra um terminal na raiz do projeto e execute:

```bash
python3 -m server.main
```

Na máquina cliente, execute:

```bash
python3 -m client.main
```

O servidor aceita o IP da interface de rede e uma porta entre `1` e `65535`. O cliente precisa do mesmo IP e da mesma porta. Use apenas os IPs das interfaces reais da rede entre as máquinas; `127.0.0.1` funciona apenas para comunicação na própria máquina.

## Executando os testes

Não são necessárias bibliotecas externas para executar o projeto ou seus testes:

```bash
python3 -m unittest discover -s tests -v
```

Os testes cobrem votos duplicados concorrentes, votos válidos e brancos, candidatos inválidos, geração do arquivo de resultado e o formato das mensagens JSON.

## Arquitetura

```text
cliente/main.py -> cliente/protocol.py -> TCP -> servidor/client_handler.py
                                                       |
                                                       v
                                              servidor/election.py
                                                       |
                                                  resultado.txt
```

O servidor mantém os candidatos, os IDs já votados e os totais em memória protegidos por um `Lock`. Cada conexão aceita é tratada por uma thread independente.

```text
votacao-eletronica/
├── server/
│   ├── main.py           Inicializa socket e apuração no terminal
│   ├── election.py       Candidatos, votos e persistência
│   ├── client_handler.py Threads de atendimento
│   ├── protocol.py       JSON, newline e validação
│   └── __init__.py
├── client/
│   ├── main.py           Menu e interação
│   ├── protocol.py       Conexão e envio
│   └── __init__.py
├── tests/test_election.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Protocolo TCP e JSON

O servidor aceita uma requisição por conexão. Cada mensagem é um objeto JSON seguido obrigatoriamente pelo caractere newline (`\n`). `receive_message()` acumula bytes com `recv()` até encontrar newline, pois uma chamada pode conter parte do JSON ou mais de uma leitura.

Requisição:

```json
{"action":"vote","student_id":"2026001","candidate_id":2}
```

Respostas:

```json
{"status":"success","message":"[VOTO CONFIRMADO]","code":"success"}
```

```json
{"status":"error","message":"Matrícula já utilizada","code":"duplicate"}
```

```json
{"status":"error","message":"Candidato inválido","code":"invalid_candidate"}
```

```json
{"status":"error","message":"Dados incompletos","code":"incomplete_data"}
```

```json
{"status":"error","message":"Dados incompletos ou JSON inválido","code":"invalid_json"}
```

```json
{"status":"error","message":"[ERRO INTERNO]","code":"internal_error"}
```

O cliente trata timeout, conexão recusada, desconexão e resposta JSON inválida como falha de comunicação.

## Instalação no Debian

```bash
sudo apt update
sudo apt install python3
cd votacao-eletronica
python3 --version
```

Não há dependências externas; `requirements.txt` documenta que somente a biblioteca padrão é necessária.

## Executando o servidor

Na VM servidor:

```bash
python3 -m server.main
```

Informe o IP real da interface da VM, por exemplo `192.168.56.10`, ou `0.0.0.0` para aceitar conexões em todas as interfaces. Informe uma porta livre, por exemplo `5000`.

Enquanto o servidor continua atendendo clientes, digite:

```text
apurar
```

Ao encerrar com `Ctrl+C`, o servidor cria `resultado.txt` no diretório atual.

## Executando clientes

Em uma ou mais VMs clientes:

```bash
python3 -m client.main
```

Informe o IP do servidor, a porta e uma matrícula. Escolha uma opção do menu. Cada cliente envia um único voto e encerra a conexão.

Exemplo:

```text
Endereço IP do servidor: 192.168.56.10
Porta do servidor: 5000
Matrícula ou ID do eleitor: 2026001
Voto recusado: Matrícula já utilizada
```

## Configuração no VirtualBox

1. Instale Debian nas VMs servidor e cliente.
2. Em **Configurações > Rede**, escolha **Rede NAT** para comunicação entre VMs da mesma rede interna, ou **Bridge** para colocá-las na rede local real.
3. **NAT** traduz o endereço das VMs e pode exigir encaminhamento de porta. **Rede NAT** permite que VMs tenham conectividade entre si sem expor diretamente as portas à rede externa. **Bridge** faz cada VM aparecer na LAN como equipamento independente.
4. Na VM servidor, identifique o endereço:

```bash
ip addr
```

Use o endereço de `enp0s3`/`eth0` que pertença à rede. Não use `127.0.0.1` para comunicação entre máquinas.

5. Teste a comunicação:

```bash
ping <IP_DO_SERVIDOR>
```

Na VM servidor, execute `python3 -m server.main`. Na(s) cliente(s), informe o IP real do servidor e execute `python3 -m client.main`.

Verifique a porta no servidor:

```bash
sudo ss -ltnp | grep 5000
```

De outra VM: `nc -vz <IP_DO_SERVIDOR> 5000` (instale `netcat-openbsd` se necessário).

## Prevenção de votos duplicados

`Election.register_vote()` adquire `_lock` antes de verificar `_voted_student_ids` e registrar a votação. A matrícula é adicionada e o contador é atualizado dentro da mesma seção crítica. Duas threads concorrentes não podem confirmar simultaneamente o mesmo ID.

## Concorrência

`socket.listen()` prepara o servidor e `accept()` cria uma conexão para cada cliente. O servidor inicia uma thread por conexão em `server/main.py`. Candidatos e IDs são compartilhados pelo objeto `Election`, protegido por `threading.Lock`. `apurar` roda no fluxo principal e não interrompe os clientes.

## Roteiro de testes

1. **Servidor:** inicie em uma VM e confirme “Servidor disponível”.
2. **Primeiro cliente:** informe matrícula única e vote em uma chapa.
3. **Voto válido:** a resposta deve conter `[VOTO CONFIRMADO]`.
4. **Segundo voto:** use a mesma matrícula em outro cliente e confirme “Matrícula já utilizada”.
5. **Concorrência:** abra vários clientes simultaneamente com matrículas diferentes.
6. **Candidato inválido:** digite, por exemplo, `9`; o cliente exibirá “Opção inválida” sem enviar o voto.
7. **Apuração:** digite `apurar` no servidor enquanto clientes continuam conectados.
8. **Encerramento:** use `Ctrl+C` e confira `resultado.txt`.
9. **Contabilização:** some candidatos e brancos e compare com o total geral.

Testes automatizados:

```bash
python3 -m unittest discover -s tests -v
```

## Explicação acadêmica

### Socket

Um socket é o ponto final de uma comunicação de rede. Neste projeto, `socket(AF_INET, SOCK_STREAM)` cria um socket TCP IPv4 em `server/main.py` e `socket.create_connection()` cria o socket do cliente em `client/protocol.py`.

### TCP

TCP estabelece uma conexão confiável e orientada a fluxo. Os dados podem chegar fragmentados ou agrupados. Por isso `receive_message()` busca o delimitador `\n` antes de decodificar JSON.

### Modelo cliente-servidor

O servidor aguarda conexões; os clientes fazem a requisição e aguardam uma resposta. A matrícula e o candidato trafegam do cliente ao servidor; o resultado trafega em sentido inverso.

### Three-way handshake

Antes dos dados, TCP realiza SYN, SYN-ACK e ACK. Essa etapa ocorre dentro de `connect()` e `accept()`.

### Funções utilizadas

- `bind()`: associa o socket servidor ao IP e à porta.
- `listen()`: coloca o socket em modo de espera.
- `accept()`: recebe uma conexão e cria um socket específico do cliente.
- `connect()`/`create_connection()`: o cliente inicia a conexão.
- `sendall()`: tenta enviar todos os bytes da mensagem.
- `recv()`: recebe pedaços do fluxo TCP.

### Threads e condições de corrida

Threads permitem atender vários clientes ao mesmo tempo. Uma condição de corrida ocorre quando operações sobre dados compartilhados podem se entrelaçar. `Lock` em `Election` transforma a verificação e o registro de voto em uma operação atômica.

### IP e porta

O endereço IP identifica a máquina na rede. A porta identifica o serviço dentro da máquina. Neste projeto o cliente precisa de `IP_DO_SERVIDOR:PORTA`.

## Checklist de requisitos

- Configuração inicial do servidor: `server/main.py`.
- Candidatos e voto branco: `server/election.py`.
- Matrículas únicas e sincronização: `Election.register_vote()` em `server/election.py`.
- Validações e respostas específicas: `server/protocol.py` e `server/client_handler.py`.
- Apuração terminal sem parar o servidor: `server/main.py` e `Election.format_tally()`.
- Conexões concorrentes: `server/main.py`.
- Cliente, menu e tratamento de falhas: `client/main.py` e `client/protocol.py`.
- JSON delimitado por newline e tolerância a fragmentação: `server/protocol.py` e `client/protocol.py`.
- Persistência em `resultado.txt`: `Election.save_result()` em `server/election.py`.
- Testes: `tests/test_election.py`.
- Documento acadêmico e instruções VirtualBox: `README.md`.

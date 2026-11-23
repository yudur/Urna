import json


MAX_MESSAGE_SIZE = 65536


def encode_message(message):
    return (json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8")


def decode_message(data):
    text = data.decode("utf-8")
    message = json.loads(text)
    if not isinstance(message, dict):
        raise ValueError("A mensagem JSON deve ser um objeto")
    return message


def receive_message(sock, buffer=b""):
    """Reads one newline-delimited JSON message and returns (message, remainder)."""
    while b"\n" not in buffer:
        if len(buffer) > MAX_MESSAGE_SIZE:
            raise ValueError("Mensagem excede o tamanho permitido")
        chunk = sock.recv(4096)
        if not chunk:
            if not buffer:
                return None, buffer
            raise ValueError("Conexão encerrada antes do fim da mensagem")
        buffer += chunk

    line, remainder = buffer.split(b"\n", 1)
    if len(line) > MAX_MESSAGE_SIZE:
        raise ValueError("Mensagem excede o tamanho permitido")
    if not line:
        raise ValueError("Mensagem vazia")
    return decode_message(line), remainder


def validate_vote_request(message):
    if not isinstance(message, dict):
        return None, "Dados incompletos"
    if message.get("action") != "vote":
        return None, "Dados incompletos"

    student_id = message.get("student_id")
    candidate_id = message.get("candidate_id")
    if not isinstance(student_id, str) or not student_id.strip():
        return None, "Dados incompletos: matrícula obrigatória"
    if isinstance(candidate_id, bool) or not isinstance(candidate_id, int):
        return None, "Dados incompletos: candidato inválido"
    return (student_id.strip(), candidate_id), None

import socket

from server.protocol import encode_message, receive_message


class CommunicationError(Exception):
    pass


def send_vote(server_host, server_port, student_id, candidate_id, timeout=5):
    try:
        with socket.create_connection((server_host, server_port), timeout=timeout) as sock:
            request = {
                "action": "vote",
                "student_id": student_id,
                "candidate_id": candidate_id,
            }
            sock.sendall(encode_message(request))
            response, _ = receive_message(sock)
            if response is None:
                raise CommunicationError("Resposta vazia do servidor")
            return response
    except CommunicationError:
        raise
    except (socket.timeout, TimeoutError):
        raise CommunicationError("Tempo limite ao aguardar resposta do servidor")
    except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError, socket.gaierror, OSError) as exc:
        raise CommunicationError(f"Falha de comunicação: {exc}")
    except ValueError as exc:
        raise CommunicationError(f"Resposta inesperada do servidor: {exc}")

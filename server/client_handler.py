from .protocol import decode_message, encode_message, receive_message, validate_vote_request


def send_response(sock, status, message, code=None):
    response = {"status": status, "message": message}
    if code:
        response["code"] = code
    sock.sendall(encode_message(response))


def handle_client(connection, address, election):
    with connection:
        try:
            message, _ = receive_message(connection)
            if message is None:
                return
            try:
                validated, error = validate_vote_request(message)
                if error:
                    send_response(connection, "error", error, "incomplete_data")
                    return
                student_id, candidate_id = validated
                confirmed, response_message, code = election.register_vote(
                    student_id, candidate_id
                )
                status = "success" if confirmed else "error"
                send_response(connection, status, response_message, code)
            except (UnicodeDecodeError, ValueError):
                send_response(connection, "error", "Dados incompletos ou JSON inválido", "invalid_json")
        except (UnicodeDecodeError, ValueError, ConnectionError):
            return
        except Exception:
            try:
                send_response(connection, "error", "[ERRO INTERNO]", "internal_error")
            except (BrokenPipeError, ConnectionError, OSError):
                pass

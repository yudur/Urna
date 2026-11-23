from .protocol import CommunicationError, send_vote


MENU = """====================================
       VOTACAO ELETRONICA
====================================

Escolha seu candidato:

1 - Chapa A
2 - Chapa B
3 - Chapa C
0 - Voto em branco

Digite sua opcao: """


def valid_port(value):
    try:
        port = int(value)
    except ValueError:
        return None
    return port if 1 <= port <= 65535 else None


def ask_configuration():
    server_host = input("Endereço IP do servidor: ").strip()
    while True:
        server_port = valid_port(input("Porta do servidor: ").strip())
        if server_port is not None:
            break
        print("Porta inválida. Digite um número entre 1 e 65535.")
    student_id = input("Matrícula ou ID do eleitor: ").strip()
    while not student_id:
        print("A matrícula não pode estar vazia.")
        student_id = input("Matrícula ou ID do eleitor: ").strip()
    return server_host, server_port, student_id


def main():
    server_host, server_port, student_id = ask_configuration()
    while True:
        choice = input(MENU).strip()
        if choice not in {"0", "1", "2", "3"}:
            print("Opção inválida. Digite 0, 1, 2 ou 3.")
            continue
        candidate_id = int(choice)
        try:
            response = send_vote(server_host, server_port, student_id, candidate_id)
        except CommunicationError as exc:
            print(str(exc))
            return

        message = response.get("message", "Resposta inesperada")
        if response.get("status") == "success":
            print(message)
        else:
            print(f"Voto recusado: {message}")
        return


if __name__ == "__main__":
    main()

import socket
import sys
import threading

from .client_handler import handle_client
from .election import Election


def valid_port(value):
    try:
        port = int(value)
    except ValueError:
        return None
    return port if 1 <= port <= 65535 else None


def ask_configuration():
    while True:
        host = input("Endereço IP do servidor: ").strip()
        try:
            socket.inet_pton(socket.AF_INET, host)
            break
        except OSError:
            print("Endereço IPv4 inválido.")
    while True:
        port = valid_port(input("Porta do servidor: ").strip())
        if port is not None:
            return host, port
        print("Porta inválida. Digite um número entre 1 e 65535.")


def run_server(host, port, election=None):
    election = election or Election()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    server_socket.settimeout(0.5)

    print(f"Servidor disponível em {host}:{port}")
    print("Digite 'apurar' para contabilizar os votos.")

    stop_event = threading.Event()

    def accept_clients():
        while not stop_event.is_set():
            try:
                connection, address = server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            thread = threading.Thread(
                target=handle_client,
                args=(connection, address, election),
                daemon=True,
            )
            thread.start()

    accept_thread = threading.Thread(target=accept_clients, daemon=True)
    accept_thread.start()
    try:
        while not stop_event.is_set():
            try:
                command = input().strip().lower()
            except EOFError:
                break
            if command == "apurar":
                print(election.format_tally())
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        stop_event.set()
        server_socket.close()
        accept_thread.join(timeout=1)
        election.save_result()
        print("Resultado salvo em resultado.txt")


def main():
    host, port = ask_configuration()
    run_server(host, port)


if __name__ == "__main__":
    main()

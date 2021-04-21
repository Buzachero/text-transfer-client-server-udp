import socket
import sys
from MetodosArquivo import MetodosArquivos
from MetodosSocket import MetodosSocket
from MetodosData import MetodosData
from constants import *



def apresentar_menu():
    print('-' * 80)
    print('O que deseja fazer?')
    print('(1) Enviar texto')
    print('(2) Receber texto')
    print('-' * 80)
    opcao = input('( ) ')
    try:
        opcao_int = int(opcao)
    except ValueError:
        opcao_int = 0
    return opcao_int


def criar_socket(host, port):
    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)  # AF_INET: ProtocoloIP | SOCK_DGRAM: ProtocoloUDP
    except socket.error as socket_error:
        print('A criação do socket falhou: {}'.format(socket_error))
        sys.exit(1)
    print('Socket criado com sucesso!')
    return client_sock


def transferir_mensagem_servidor(client_sock, server_host, server_port):
    server_host_port = '{}:{}'.format(server_host, server_port)

    opcao = 0
    while int(opcao) != 1 and int(opcao) != 2:
        opcao = apresentar_menu()

    MetodosSocket.enviar_texto(AUTHORIZATION_KEY + str(opcao), client_sock, (server_host, server_port))
    print('Opcao {} enviada para {} ...'.format(opcao, server_host_port))
    if int(opcao) == 1:
        texto_arquivo = MetodosArquivos.ler_conteudo_arquivo(CLIENT_FILE_PATH)
        print('Enviando texto para {} ...'.format(server_host_port), end=' ')
        MetodosSocket.enviar_texto(AUTHORIZATION_KEY + texto_arquivo, client_sock, (server_host, server_port))
        print('Texto enviado!')
        texto_recebido = MetodosSocket.receber_texto(client_sock)
        print(texto_recebido)
    if int(opcao) == 2:
        texto_recebido = MetodosSocket.receber_texto(client_sock)
        print(MetodosData.prefixar_com_data_hora_atual('Texto recebido do host {} --> '.format(server_host_port)), end=' ')
        sucesso = MetodosArquivos.escrever_dados_arquivo(CLIENT_FILE_PATH, texto_recebido)
        mensagem = 'Sucesso na gravação do texto no arquivo do cliente!' if sucesso \
            else 'Houve alguma falha na gravação do texto no arquivo do cliente!'
        MetodosSocket.enviar_texto(AUTHORIZATION_KEY + mensagem, client_sock, (server_host, server_port))


if __name__ == '__main__':
    server_host = SERVER_HOST
    server_port = PORT
    args = sys.argv
    if len(args) == 2:
        server_host = args[1]
    elif len(args) == 3:
        server_host = args[1]
        try:
            server_port = int(args[2])
        except ValueError:
            print('A porta do servidor nao é um número!')
            sys.exit(1)
    try:
        client_sock = criar_socket(server_host, server_port)
        transferir_mensagem_servidor(client_sock, server_host, server_port)
    except KeyboardInterrupt:
        print('Aplicação encerrada pelo usuário ou sistema!')
    finally:
        client_sock.close()
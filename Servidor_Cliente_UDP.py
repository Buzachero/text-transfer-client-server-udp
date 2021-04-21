import socket
import sys
from MetodosArquivo import MetodosArquivos
from MetodosSocket import MetodosSocket
from MetodosData import MetodosData
from constants import *


def validar_mensagem(mensagem):
    is_mensagem_valida = True
    if len(mensagem) < len(AUTHENTICATION_KEY):
        is_mensagem_valida = False
    if not mensagem.startswith(AUTHENTICATION_KEY):
        is_mensagem_valida = False
        print(MetodosData.prefixar_com_data_hora_atual(f'Chave inválida! Envio de dados pelo host {host} não autorizado!'))
    return is_mensagem_valida

def validar_host_origem(host):
    is_host_valido = True
    if not host.startswith(PREFIX_IP_ALLOWED):
        is_host_valido = False
        print(MetodosData.prefixar_com_data_hora_atual(f'Host negado! Envio de dados pelo host {host} não autorizado!'))
    return is_host_valido

def formatar_mensagem_sem_chave(mensagem):
    if len(mensagem) < len(AUTHENTICATION_KEY):
        return mensagem
    return mensagem[len(AUTHENTICATION_KEY):len(mensagem)]

def transferir_mensagem_cliente(sock):
    try:
        dados, endereco_cliente = MetodosSocket.receber_texto_endereco_origem(sock)
        host = endereco_cliente[0]
        port = endereco_cliente[1]
        if not validar_host_origem(host) \
            or not validar_mensagem(dados):
            return
        opcao_str = formatar_mensagem_sem_chave(dados)
        try:
            opcao = int(opcao_str)
        except ValueError:
            return
        opcao_msg = 'enviar texto para' if opcao == 1 else 'receber texto do'
        print(MetodosData.prefixar_com_data_hora_atual('Host {} deseja {} servidor'.format(host, opcao_msg)))
        if opcao == 1:
            texto_recebido, endereco_cliente = MetodosSocket.receber_texto_endereco_origem(sock)
            if not validar_host_origem(endereco_cliente[0]) \
                    or not validar_mensagem(texto_recebido):
                return
            print(MetodosData.prefixar_com_data_hora_atual('Texto recebido do host {} --> '.format(host)), end=' ')
            texto_arquivo = formatar_mensagem_sem_chave(texto_recebido)
            sucesso = MetodosArquivos.escrever_dados_arquivo(SERVER_FILE_PATH, texto_arquivo)
            mensagem = 'Sucesso na gravação do texto no arquivo do servidor!' if sucesso \
                else 'Houve alguma falha na gravação do texto no arquivo do servidor!'
            MetodosSocket.enviar_texto(MetodosData.prefixar_com_data_hora_atual(mensagem), sock, endereco_cliente)
        elif opcao == 2:
            texto_arquivo = MetodosArquivos.ler_conteudo_arquivo(SERVER_FILE_PATH)
            client_host_port = '{}:{}'.format(host, port)
            print(MetodosData.prefixar_com_data_hora_atual('Enviando texto  para {} ...'.format(client_host_port)), end=' ')
            MetodosSocket.enviar_texto(texto_arquivo, sock, endereco_cliente)
            print('Texto enviado!')
            texto_recebido = MetodosSocket.receber_texto(sock)
            resposta = formatar_mensagem_sem_chave(texto_recebido)
            print(MetodosData.prefixar_com_data_hora_atual(resposta))
        else:
            print('Opcao desconhecida : {}'.format(opcao))
    except ConnectionResetError as conn_error:
        print('Conexão perdida! Erro: {}'.format(conn_error))


def criar_socket_bind(server_host, server_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_host, server_port))
    return sock


if __name__ == '__main__':
    host = SERVER_HOST
    port = PORT
    args = sys.argv
    if len(args) == 2:
        host = args[1]
    elif len(args) == 3:
        host = args[1]
        try:
            port = int(args[2])
        except ValueError:
            print('A porta do servidor nao é um número!')
            sys.exit(1)

    server_socket = criar_socket_bind(host, port)
    print('Socket criado com sucesso!')
    print('-' * 80)
    try:
        while True:
            print('Esperando envio de dados na porta {} ...'.format(port))
            transferir_mensagem_cliente(server_socket)
            print('-' * 80)
    except KeyboardInterrupt:
        print('Aplicação encerrada pelo usuário ou sistema!')
    finally:
        server_socket.close()

#!/usr/bin/python3
import socket
import sys
import threading
import os

class Cliente:
	'''Usuário do bate-papo'''

	def __init__(self, host = '127.0.0.1', port = 9999):
		'''Inicializa as variáveis iniciais do cliente'''
		self.host = host
		self.port = port


	def envia_mensagem(self):
		'''Envia mensagem ao servidor'''

		try:
			while True:
				msg = input()
				self.s.send(msg.encode('utf-8'))
				is_saida = msg.split() #Coloca as substrings da mensagem numa lista
				if not is_saida:
					continue 
				if is_saida[0] == '/tchau':
					self.s.close()
					os._exit(1)
		except: #Trata o CTRL+C
			msg = '/tchau'
			self.s.send(msg.encode('utf-8'))
			self.s.close()
			os._exit(1)

	def recebe_mensagem(self):
		'''Recebe mensagem do servidor'''
		while True:
			msg = self.s.recv(4096).decode('utf-8')
			if msg == '/SERVIDOR_OFF': #Servidor por algum motivo encerrou
				print('Encerrando conexão, servidor está OFF.')
				self.s.close()
				os._exit(1)			
			if msg.startswith('/BANIDO'):
				print(' '.join(msg.split()[1:]))
				self.s.close()
				os._exit(1)

			print (msg)


	def main(self):
		'''Começa a execução do cliente, conecta socket TCP '''

		self.cria_conexao_tcp()
		
		thread = threading.Thread(target = self.recebe_mensagem)
		thread.start()

		self.envia_mensagem()
		
	def cria_conexao_tcp(self):
		'''Cria conexão TCP com o servidor'''
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#Cria a conexão TCP 
		except:
			print('Erro ao criar o socket')
			os._exit(1)

		dest = (self.host, self.port)
		try:
			self.s.connect(dest)	#conecta ao servidor
		except:
			print("Servidor não está conectado no momento.")
			sys.exit()

if __name__ == "__main__":
	cliente = Cliente()
	cliente.main()
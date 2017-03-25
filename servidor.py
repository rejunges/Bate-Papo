#!/usr/bin/python3
import socket
import sys
import threading
import os
import time

class Servidor:
	'''Serve como servidor de um bate papo. Essa classe é responsável por gerenciar as mensagens que chegam dos clientes
	e envia-la a outros clientes.'''

	def __init__(self, host = '', port = 9999):
		'''Inicializa as variáveis iniciais do servidor'''

		self.finaliza = '/SERVIDOR_OFF'
		self.banido = '/BANIDO'
		self.host = host
		self.port = port
		self.palavras_reservadas = ['tchau', '/tchau', 'lista_online', '/lista_online', 'lista_bloqueados',
		 '/lista_bloqueados', 'bloquear', '/bloquear', 'desbloquear', '/desbloquear',
		  'SERVIDOR_OFF', '/SERVIDOR_OFF', 'BANIDO', '/BANIDO']
		self.clientes = {} #key: apelido. Value: (con, [bloqueados], [quem_me_bloqueou])

	def main(self):
		'''Começa a execução do servidor, aqui as threads são inicializadas e enviadas aos respectivos métodos'''
		
		try:
			self.cria_conexao_tcp()
			self.aceita_conexao_clientes()
		except:
			self.envia_mensagem_publica([], self.finaliza, 1)
			os._exit(1)

	def cria_conexao_tcp(self):
		'''Cria uma conexão TCP '''

		dest = (self.host, self.port)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		try:
			#Vincula socket a um endereço particular e porta
			self.s.bind(dest)
		except:
			print ('Bind falhou')
			os._exit(1)

		self.s.listen(5)

	def encerra_conexao_tcp(self):
		'''Encerra a conexão TCP'''

		self.s.close()

	def verifica_apelido(self, novo_apelido):
		'''Verifica se já existe o apelido no chat e se não é uma palavra reservada/regra.
		Se já existir retorna True se não retorna False'''
		if novo_apelido in self.palavras_reservadas:
			return True

		return novo_apelido in self.clientes

	def comando_msg(self, remetente, msg):
		'''Verifica se a mensagem enviada é um comando/regra ou se é mensagem pública.

		Lista de comandos:
		/tchau				#Cliente encerra conexão com servidor
		/bloquear apelido         #Cliente bloqueia fulano que tem o nome escrito em apelido
		/desbloquear apelido        #Cliente desbloqueia fulano que tem o nome escrito em apelido
		/lista_bloqueados			#Mostra uma lista de bloqueados
		/lista_online				#Mosta uma lista com todos os usuários do chat
		/apelido 			#Cliente manda mensagem privada para fulado que tem o nome escrito em apelido'''

		is_comando = msg.strip() #Tira espaços em branco no início e fim da mensagem
		is_comando = list(is_comando) #Coloca numa lista todas as letras da mensagem

		if is_comando[0] == '/':
			is_comando = msg.split() #Coloca as substrings da mensagem numa lista

			if is_comando[0] == '/tchau':
				print('{} saiu do bate-papo.'.format(remetente))
				self.fim_conexao(remetente)

			elif is_comando[0] == '/bloquear' or is_comando[0] == '/desbloquear':
				try:
					bloqueado = self.pega_apelido(' '.join(is_comando[1:]))
				except:
					msg = 'Digite o nome de quem deseja bloquear/desbloquear após o comando.\n Ex: /bloquear fulano'
					self.envia_mensagem_privada([], remetente, msg)
					return
				
				#Verifica se existe esse usuário
				if not self.verifica_apelido(bloqueado):
					msg = 'O usuário não está conectado.'
					self.envia_mensagem_privada([], remetente, msg)
					return

				if is_comando[0] == '/bloquear':
					self.bloquear_usuario(remetente, bloqueado)
	
				else:
					self.desbloquear_usuario(remetente, bloqueado)
			
			elif is_comando[0] == '/lista_bloqueados':
				msg = self.lista_bloqueados(remetente)
				self.envia_mensagem_privada([], remetente, msg)

			elif is_comando[0] == '/lista_online':
				msg = self.lista_online()
				self.envia_mensagem_privada([], remetente, msg)

			else:
				#É uma mensagem privada
				destinatario = self.pega_apelido(msg[1:])

				if self.verifica_apelido(destinatario):
					msg = msg.replace('/' + destinatario, '')
					self.envia_mensagem_privada(remetente, destinatario, msg)
				else:
					msg = 'Não foi possível enviar a mensagem para o destinatário desejado, pois esse usuário não está conectado no bate-papo.'
					self.envia_mensagem_privada([], remetente, msg)
					return

		else:
			#É uma mensagem pública
			self.envia_mensagem_publica(remetente, msg)

	def pega_apelido(self, nome):
		'''Para comandos de bloquear, desbloquear e mandar privado, essa função retorna o apelido da pessoa'''
		
		destinatario = ''

		for apelido in self.clientes:
			if nome.startswith(apelido):
				destinatario = apelido
				break

		return destinatario

	def lista_online(self):
		'''Lista de usuários online no chat. Retorna string formatada para envio ao cliente'''

		online = 'Lista de clientes conectados no bate-papo no momento:\n'
		for clientes in list(self.clientes.keys()):
			online = online + clientes + '\n'

		return online[:-1]

	def lista_bloqueados(self, usuario):
		'''Lista de bloqueados do usuário passado por parâmetro. Retorna string formatada para envio ao cliente'''

		bloqueados = 'Sua lista de usuários bloqueados:\n'
		con, list_bloq, qm_bloqueou = self.clientes.get(usuario)

		if not list_bloq:
			return 'Não tem nenhum usuário até o momento.' 
		
		for bloqueado in list_bloq:
			bloqueados =  bloqueados + bloqueado + '\n'

		return bloqueados[:-1]


	def desbloquear_usuario(self, usuario, bloqueado):
		'''Usuario é quem quer desbloquear, e bloqueado é quem deve ser desbloqueado'''

		if usuario == bloqueado or not self.verifica_bloqueio(usuario, bloqueado):
			msg = 'O usuário que deseja desbloquear não está bloqueado.'
			self.envia_mensagem_privada([], usuario, msg)
			return
		
		con, bloqueados, quem_bloq = self.clientes.get(usuario)
		del bloqueados[bloqueados.index(bloqueado)]
		con, bloqueados, quem_bloq = self.clientes.get(bloqueado)
		del quem_bloq[quem_bloq.index(usuario)]

		print('{0} desbloqueou {1}.'.format(usuario, bloqueado))
		msg = 'Você desbloqueou ' + bloqueado + '.'
		self.envia_mensagem_privada([], usuario, msg)

		msg = 'Você foi desbloqueado por ' + usuario + '.'
		self.envia_mensagem_privada([], bloqueado, msg)


	def bloquear_usuario(self, usuario, bloqueado):
		'''Usuario é quem quer bloquear, e bloqueado é quem deve ser bloqueado'''
		
		if usuario == bloqueado:
			msg = 'Não é possível se auto-bloquear.'
			self.envia_mensagem_privada([], usuario, msg)
			return

		if self.verifica_bloqueio(usuario, bloqueado):
			msg = 'O usuário que deseja bloquear já está bloqueado.'
			self.envia_mensagem_privada([], usuario, msg)

		con, bloqueados, quem_bloq = self.clientes.get(usuario)
		bloqueados.append(bloqueado)
		con, bloqueados, quem_bloq = self.clientes.get(bloqueado)
		quem_bloq.append(usuario)

		print('{0} bloqueou {1}.'.format(usuario, bloqueado))

		msg = 'Você bloqueou ' + bloqueado + '.'
		self.envia_mensagem_privada([], usuario, msg)

		msg = 'Você foi bloqueado por ' + usuario + '.'
		self.envia_mensagem_privada([], bloqueado, msg)

		#Se tem mais de 2 pessoas conectadas, e o usuário foi bloqueado por todas, ele é retirado do bate-papo
		if len(self.clientes) > 2 and (len(self.clientes) - 1) ==  len(quem_bloq):
			msg = self.banido + ' Você foi banido do bate-papo pois todos os usuários te bloquearam.'
			time.sleep(0.5)
			self.envia_mensagem_privada([], bloqueado, msg)
			print('{} foi retirado do bate-papo.'.format(bloqueado))
			self.fim_conexao(bloqueado, True)

	def verifica_bloqueio(self, usuario, bloqueado):
		'''Verifica se bloqueado já está bloqueado pelo usuario. Retorna True se estiver, False caso contário'''

		con, bloqueados, quem_bloq = self.clientes.get(usuario)
		
		if bloqueado in bloqueados:
			return True

		return False

	def recebe_mensagem(self, apelido, con):
		'''Recebe mensagem do usuário'''

		while True:
			try:
				msg = con.recv(4026).decode('utf-8')
				self.comando_msg(apelido, msg)
			except:
				break

	def controle_conexao(self, con):
		'''Faz o controle de conexão de cada cliente. Cada cliente é executado por uma thread a partir desse ponto'''
		
		con.send('Bem-vindo ao bate-papo Rêssenger! Digite seu apelido:'.encode('utf-8'))
		apelido = con.recv(1024).decode('utf-8')
		
		#Verifica se o apelido é válido
		existe = self.verifica_apelido(apelido)
		while existe:
			con.send('Desculpa, esse apelido já está sendo usado por outra pessoa ou é um comando no bate-papo e não deve ser usado. Tente outro apelido:'.encode('utf-8'))
			apelido = con.recv(1024).decode('utf-8')
			existe = self.verifica_apelido(apelido)

		print("{} conectou-se ao bate-papo Rêssenger.".format(apelido))

		#key: apelido. Value: (con, [bloqueados], [quem_me_bloqueou])
		self.clientes[apelido] = (con, [], [])		

		msg = 'entrou no bate-papo.'
		self.envia_mensagem_publica(apelido, msg, 1)
		self.recebe_mensagem(apelido, con)

	def encerra_todas_conexoes(self):
		'''Encerra o socket aberto com todos os clientes'''

		for apelido, value in list(self.clientes.items()):
			con, bloq, qm_bloq = value
			con.close()

	def envia_mensagem_publica(self, remetente, msg, flag = 0):
		'''Envia mensagens para todos os clientes, exceto para cliente bloqueado por alguém.
		flag por default é inicializada em 0 o que significa que é um cliente que quer enviar a mensagem. 
		Se a flag for 1 significa que é o servidor que está enviando a mensagem'''

		def envia_mensagem_para_todos():
			#value: (con, [bloqueados], [qm_bloqueou]]

			for apelido, value in list(self.clientes.items()):
				conn, bloq, qm_bloq = value
				#Verifica que o usuario que irá receber a mensagem não é o mesmo que envia a mensagem.
				#Verifica que não está bloqueado pelo remetente
				#Verifica se o usuário que irá receber a mensagem não bloqueou o usuário remetente.
				if apelido != remetente and not apelido in bloqueados and not apelido in list_quem_bloqueou:
					self.envio_mensagem(conn, apelido, msg)

		if not self.clientes: #Servidor vai fechar e não tem ninguém conectado
			return

		bloqueados = []
		list_quem_bloqueou = []
		
		if flag:
			if not remetente:
				envia_mensagem_para_todos()
				self.encerra_todas_conexoes()
			else:
				msg = remetente + ' ' + msg
		else:
			msg = '<'+ remetente + '> ' + msg
			con, bloqueados, list_quem_bloqueou = self.clientes.get(remetente)

		envia_mensagem_para_todos()


	def envia_mensagem_privada(self, remetente, destinatario, msg):
		'''Envia mensagem de um cliente para um único usuário'''
		

		con, bloq_dest, qm_bloq_dest = self.clientes.get(destinatario)

		if remetente != []:
			#Verifica se o remetente não bloqueou o destinatário, ou o destinatário não bloqueou o cliente
			if remetente in qm_bloq_dest:
				msg = 'Você bloqueou  ' + destinatario + ' anteriormente. Não é possível enviar a mensagem.'
				self.envia_mensagem_privada([], remetente, msg)
				return
			
			if remetente in bloq_dest:
				msg = 'Não é possível enviar mensagens à ' + destinatario + ' pois você está bloqueado.'
				self.envia_mensagem_privada([], remetente, msg)
				return

			if remetente == destinatario:
				msg = 'Você não pode enviar mensagens privadas a si mesmo.'
			else:
				#Envia mensagem privada
				msg = '<' + remetente + '> <Privado> ' + msg

		self.envio_mensagem(con, destinatario, msg)


	def envio_mensagem(self, con, apelido, msg):
		'''Esse método é chamado internamente pela função envia_mensagem_publica e envia_mensagem_privada.
		Ele envia através do socket(con) a mensagem ao destinatário.
		Caso a mensagem não consiga ser enviada(erro no socket), o destinatário tem sua conexão encerrada'''

		try:
			con.send(msg.encode('utf-8'))
		except:
			pass

	def fim_conexao(self, apelido, banido = 0):
		'''Esse método é chamado internamente pela encerrar conexão de um cliente.'''

		#Pega conexão que será encerrada
		con, bloqueados, quem_bloq = self.clientes.get(apelido)
		
		#desbloqueia todos os usuários bloqueados e sai da lista de bloqueados dos outros usuários e de quem bloqueou também
		for bloqueado in bloqueados:
			conn, list_bloq, list_quem_bloq = self.clientes.get(bloqueado)
			del list_quem_bloq[list_quem_bloq.index(usuario)]
		
		for bloqueador in quem_bloq:
			conn, list_bloq, list_quem_bloq = self.clientes.get(bloqueador)
			del list_bloq[list_bloq.index(apelido)]

		#Remove do dicionário
		del self.clientes[apelido]

		if banido:
			msg = 'foi banido(a) e por isso foi desconectado do bate-papo.'
		else:
			msg = 'saiu do bate-papo.'
		self.envia_mensagem_publica(apelido, msg, 1)
		con.close()

	def aceita_conexao_clientes(self):
		'''Aceita conexão de clientes que se conectam ao servidor'''

		while True:
			con, addr = self.s.accept()
			thread = threading.Thread(target = self.controle_conexao, args = (con,))
			thread.start()

if __name__ == "__main__":
	server = Servidor()
	server.main()
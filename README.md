# Bate-Papo

Bate-Papo desenvolvido para a disciplina de Redes de Computadores na Universidade Federal de Pelotas. Funciona em rede local com o uso de sockets
O trabalho foi implementado na estrutura cliente-servidor.
O código foi desenvolvido na linguagem Python, versão 3.

#Inicialização do bate-papo:

Para inicializar o bate-papo é necessário primeiramente abrir o servidor, e após isso abrir um ou mais clientes.

Se o python 3 é default na máquina utilizada o servidor pode ser aberto com o seguinte comando:
		python servidor.py
Se o python 3 não é default é necessário utilizar o comando:
		python3 servidor.py
O mesmo segue para abrir um ou mais clientes:
		python cliente.py
			ou
		python3 cliente.py

#Funcionamento do bate-papo:

	Funcionamento do servidor:
		O servidor é responsável por receber as mensagens dos clientes e a partir disso verificar se ela é um comando (bloquear, desbloquear, enviar mensagem privada, lista de onlines, lista de bloqueados, sair). Além disso, o servidor deve manter o correto funcionamento do bate-papo, executando o comando que é pedido pelo cliente ou enviando mensagem de um deles para todos os outros.

	Funcionamento do cliente:
		Quando o cliente se conecta ao servidor, ele deve informar seu nome/apelido, sendo que este não pode ser igual ao nome/apelido de nenhum dos usuários que estão conectados no momento.
		O cliente pode mandar tanto mensagens públicas quanto mensagens privadas. Além disso, ele pode bloquear e desbloquear usuários, ver lista de clientes conectados no bate-papo no presente momento e visualizar a lista de usuários que estão bloqueados.

#Comandos que podem ser usados pelo cliente:

	/tchau 
		O comando /tchau é usado pelo cliente quando este quer se retirar do bate-papo. Caso o cliente dê um Ctrl + C no terminal, ele também é desconectado corretamente do bate-papo pois envia, por default, o /tchau para o servidor. 
		
	/bloquear usuario
		O comando /bloquear é usado para bloquear um usuário, no lugar de 'usuário' deve-se colocar o nome do usuário que será bloqueado. O usuário que foi bloqueado recebe mensagem de aviso sobre isso.

	/desbloquear usuario
		O comando /desbloquear é usado para desbloquear um usuário, no lugar de 'usuário' deve-se colocar o nome do usuário que será desbloqueado. O usuário que foi desbloqueado recebe mensagem de aviso sobre isso.

	/lista_bloqueados
		O comando /lista_bloqueados é usado para ver a lista de usuários que foram bloqueados pelo próprio cliente na sessão corrente.

	/lista_online
		O comando /lista_online é usado para ter acesso a lista de usuários que estão conectados no bate-papo no presente momento.

	/apelido
		O comando /apelido é usado para enviar mensagem privada, no lugar de apelido deve-se escrever o nome/apelido do usuário.

#Informações gerais:

Se o bate-papo possuir mais de dois usuários conectados, e o usuário Y for bloqueado por todos os outros usuários, ele é instantaneamente banido do bate-papo, ou seja, ele é desconectado.
No servidor é mostrado ações importantes que estão acontecendo no bate-papo, tais como: conexão de usuário, fim de conexão, ações de bloqueio e desbloqueio.
Se o servidor for fechado, todos os clientes são automaticamente desconectados da aplicação.

#Exemplos de uso:

Se o bate-papo tem três usuários conectados - Alice, Bob e Trudy - e Alice quer mandar mensagem para o Bob ela deve enviar a seguinte linha:
		
	/Bob Oi, como tá? Tenho um super segredo para contar!

Se Bob quiser responder privado, para Alice ele pode dizer:

	/Alice Oi! Conta, o que é?!

E enquanto isso Trudy não sabe quem está no bate papo então ela usa o seguinte comando para receber a lista de usuários conectados:

	/lista_conectados

A partir disso a Trudy sabe que tanto Bob e Alice estão online então ela envia uma mensagem pública:

	Oi Bob! Oi Alice! Cliquem nesse link para mudar a cor do facebook!

Tanto Bob quanto Alice resolvem bloquear Trudy pois ela é inconveniente, então ambos vão escrever:

	/bloquear Trudy

Como todos os usuários do bate-papo bloquearam Trudy ela foi banida do sistema e agora não vai mais importunar as pessoas!

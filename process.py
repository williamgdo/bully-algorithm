# authors
# Jose Gabriel de Oliveira Santana 620459
# William Giacometti Dutra de Oliveira 743606

import socket
import sys
import struct
import threading
import pickle
import time
import random

# Funcionamento: #######################
# rodar 5 processos com portas de 2020 ate 2025 e IDs iniciados de 1 a 5

multicast_group = '225.0.0.1'       # configura o ip hospedeiro para a conexao
multicast_port = 2022               # porta de comunicacao (a mesma que a do servidor)
leader = 4                          # id do processo lider default
processCount = 4                    # numero de processos simultaneos
TIMEOUT = 5                         # timeout em segundos        

p_id = -1       
P_PORT = -1       

def create_multicast():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(('', P_PORT))
  mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
  
  return sock


def send_multicast(s_t, msg):
  # time.sleep(random.randint(3, 10))
  s_t.sendto(pickle.dumps(msg), (multicast_group, multicast_port))
  time.sleep(2)
    
def send(s_t, msg, port):
  s_t.sendto(pickle.dumps(msg), (multicast_group, port))

def getProcessId(port):
    return str(port[-1:])

def getProcessPort(p_id):
    return 2020 + int(p_id)

def announceCoordinator(clock, s_t):
  for i in range(1, processCount + 1): # starts in p_id stops in processCount
    msg = ["coordenador", clock[0]+1, p_id, True]
    send(s_t, msg, getProcessPort(i))
    clock[0] = clock[0]+1
    
def announceElection(clock, s_t):
  for i in range(p_id + 1, processCount + 1): # starts in 1 stops in processCount
    if(p_id == i):
        continue
      
    # print("enviando msg para ", i, getProcessPort(i))
    msg = ["eleicao", clock[0]+1, p_id, True]
    send(s_t, msg, getProcessPort(i))
    clock[0] = clock[0]+1
    
    
  s_t.settimeout(TIMEOUT)
  print("Esperando pelo menos um ACK por " + str(TIMEOUT) + " segundos")
  
  while True:
    try:
      msg = pickle.loads(s_t.recv( 1024 ))
      if msg[0] == "ACK":  
        print("Um ID maior respondeu minha eleicao: ", msg)
        print("Desistindo...")
        break
      
    except socket.timeout: 
      print("Nenhum processo respondeu minha eleicao, logo sou o novo lider")
      announceCoordinator(clock, s_t)
      break  
    finally:
      s_t.settimeout(None)
    
    
def listen (p_id, msg_list, clock):
  global leader

  s_t = create_multicast()

  while True:
      
      # time.sleep(random.randint(3, 10))
      time.sleep(2)

      msg = pickle.loads(s_t.recv( 1024 ))
      
      if(msg[1] > clock[0]):
          clock[0] = msg[1]+1
      else:
          clock[0] = clock[0]+1

      if(msg[3] == True):
          # print("Mensagem recebida: ", msg)
          msg_list.append(msg)

          msg_list.sort(key = lambda x: (x[1], x[2]))
          
          # time.sleep(3)
          # print("Lista de msgs: ----->")
          # print(msg_list)
          # print("-------------------->")

          # ack = ["ACK", clock[0], p_id, False]
          # send(s_t, ack, getProcessPort(msg[2]))


          if msg[0] == "eleicao": 
            print(str(msg[2]) + " convocou a eleicao")
            
            if p_id > msg[2]:
              print("Meu ID é maior.")
              ack = ["ACK", clock[0], p_id, False]
              send(s_t, ack, getProcessPort(msg[2]))
              # TODO: convocar eleicao
              announceElection(clock, s_t)
                
          if msg[0] == "coordenador": 
            print(str(msg[2]) + " se tornou lider")
            
            leader = msg[2]
                
      else:
          print("ACK recebido: ", msg)

def Main(argv):
  global p_id, P_PORT
  
  if len(sys.argv) == 2:
    # multicast_port = int(argv[1])
    p_id = int(argv[1])
    # clock = [int(argv[3])]
  else:
    p_id = input("Id do processo: ")
    # clock = input("Clock inicial: ")

  P_PORT = getProcessPort(p_id)

  s_t = create_multicast()

  msg_list = []

  # p_id = int(p_id)
  # clock = [int(clock)]
  clock = [0]


  t_proc = threading.Thread(target=listen, args=(p_id, msg_list, clock))

  t_proc.start()

  while True:
      input()
      userInput = input("Convocar eleicao (c), mostrar lider (l): ")
      
      if userInput == "c": 
        print("Convocando...")
        announceElection(clock, s_t)
        
      if userInput == "l": 
        print("Lider atual: ", str(leader))



if __name__ == '__main__':
    Main(sys.argv)

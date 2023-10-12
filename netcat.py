import argparse #parse the arguments to check the flags and the corresponding options. 
import socket #Tcp connectiviry to another host in the netwrok
import shlex #this is parser that will help us parse the code, extreamly helpful with text with nested quotes. passing a single string would not handle spaces and special charchters really well.
import subprocess # create a subprocess on the system
import sys # to run system commands 
import textwrap # to wrap the output. very handy in command line apps 
import threading # multi threding functionality 

def execute(cmd):
    cmd = cmd.strip() # the strip is going to remove the whitespace in the beginging and end of a string. This is built-in method. 
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT) #if there is a command, create a subprocess and get the cmd from it. subprocess.check_output() runs the specified command and captures the output. if there is an error the value
    # is stored in the stderr, we just move this value to the standard output 
    return output.decode()

class Netcat:
    """docstring for Netcat:."""
    def __init__(self, args,buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def  send(self):
        self.socket.connect((self.args.target , self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
            try:
                while True:
                    recv_len = 1
                    response = ''
                    while recv_len:
                        data = self.socket.recv(4096)#recieve 4096 bytes if date
                        recv_len = len(data)
                        response += data.decode()# we append the receive data to the response
                        if recv_len < 4096:#we keep appending until ther is no more data to process.
                            break
                        if response:
                            print(response)# we are going to print the respons
                            buffer = input('>')
                            buffer += '/n'
                            self.socket.send(buffer.encode())
            except KeyboardInterrupt:#we keep doing this until the user terminates this
                print("User terminated.")
                self.socket.close()
                sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)#support up to 5 connectinos at once 
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        
        elif self.args.upload:#each elif corresponds to a flag in the command 
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                    print(len(file_buffer))
                else:
                    break

            with open(self.args.upload, 'wb' ) as f:
                f.write(file_buffer)
            message = f'saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b' #> ')
                    while '\n' not in cmd_buffer.decode():#it is constantly looking for the new line charecter.
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()
                        

            

        

if __name__ == "__main__": # this code runs if we run netcat. this will not run if someone importa the code into their code. 
    parser = argparse.ArgumentParser(
            description='Tool',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=textwrap.dedent('''Example:
                                   netcat.py -t 192.168.1.1 -p 5555 -l -c 
                                   netcat.py -t 192.168.1.1 -p 5555 -l -u=mytest.txt 
                                   netcat.py -t 192.168.1.1 -p 5555 -l -e=\"cat /etc/passwd\" 
                                   echo 'ABC' | ./netcat.py -t 192.68.1.1 -p 135 
                                   netcat.py -t 192.168.1.1 -p 555 
                                   ''')
            )
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='executes specific command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.1', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()

    if args.listen: #if it is in listener mode, empty the buffer
        buffer = ''
    else:# if not read the input from the standard input
        buffer = sys.stdin.read()

    nc = Netcat(args, buffer.encode()) #pass data into the network class
    nc.run() #use the subprocess module to run the calss
#the 16:00 min

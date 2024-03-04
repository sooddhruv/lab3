import pickle
import socket
import requests
from flask import Flask, request

app = Flask(__name__)

BUFFER_SIZE = 2048

@app.route('/')
def introduction_US():
    return 'This is User Server - US'

@app.route('/fibonacci', methods=["GET"])
def fibonacci():
    as_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = request.args.get('hostname').replace('"', '')
    fs_port = int(request.args.get('fs_port'))
    number = int(request.args.get('number'))
    as_ip = request.args.get('as_ip').replace('"', '')
    as_port = int(request.args.get('as_port'))

    # Request Fibonacci server information from authoritative server
    as_socket.sendto(pickle.dumps(("A", hostname)), (as_ip, as_port))
    response, _ = as_socket.recvfrom(BUFFER_SIZE)
    response = pickle.loads(response)

    type, hostname, fs_ip, ttl = response

    if not fs_ip:
        return "Couldn't retrieve fs_ip"

    # Request Fibonacci number from the Fibonacci server
    fs_url = f"http://{fs_ip}:{fs_port}/fibonacci"
    response = requests.get(fs_url, params={"number": number})

    return response.content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

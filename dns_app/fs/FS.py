import socket
import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

BUFFER_SIZE = 1024

@app.route('/')
def introduction_FS():
    return "This is Fibonacci Server (FS)"

def get_fib(n):
    if n < 0:
        raise ValueError("n should be greater than 0")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return get_fib(n - 1) + get_fib(n - 2)

@app.route('/fibonacci')
def fibonacci():
    n = int(request.args.get('number'))
    return str(get_fib(n))

@app.route('/register', methods=['PUT'])
def register():
    body = request.json
    if not body:
        return jsonify({"error": "Body is None"}), 400

    hostname = body.get("hostname")
    fs_ip = body.get("fs_ip")
    as_ip = body.get("as_ip")
    as_port = body.get("as_port")
    ttl = body.get("ttl")

    if None in (hostname, fs_ip, as_ip, as_port, ttl):
        return jsonify({"error": "Missing fields in the request"}), 400

    msg = (hostname, fs_ip, "A", ttl)
    msg_bytes = pickle.dumps(msg)

    as_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    as_socket.sendto(msg_bytes, (as_ip, as_port))

    return "Registration Successful!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)

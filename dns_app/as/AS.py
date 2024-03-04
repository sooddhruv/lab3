import socket
import pickle
import json
import time
import os
import logging as log

log.basicConfig(
    format='[%(asctime)s %(filename)s:%(lineno)d] %(message)s',
    datefmt='%I:%M:%S %p',
    level=log.DEBUG
)

# Constants
HOST_IP = "0.0.0.0"
SERVER_PORT = 53533
BUFFER_SIZE = 1024
AUTH_SERVER_DB_FILE = "/tmp/auth_db.json"
TYPE = "A"


def initialize_auth_db():
    if not os.path.exists(AUTH_SERVER_DB_FILE):
        with open(AUTH_SERVER_DB_FILE, "w") as f:
            json.dump({}, f, indent=4)


def save_dns_record(name, value, ttl):
    with open(AUTH_SERVER_DB_FILE, "r") as f:
        existing_records = json.load(f)

    ttl_ts = time.time() + int(ttl)

    existing_records[name] = (value, ttl_ts, ttl)

    with open(AUTH_SERVER_DB_FILE, "w") as f:
        json.dump(existing_records, f, indent=4)
        log.debug(f"Saving DNS record for {name} {(value, ttl_ts, ttl)}")


def get_dns_record(name):
    with open(AUTH_SERVER_DB_FILE, "r") as f:
        existing_records = json.load(f)

    dns_record = existing_records.get(name)

    if not dns_record:
        log.info(f"No DNS record found for {name}")
        return None

    value, ttl_ts, ttl = dns_record
    log.debug(f"Got DNS records for {name}: {dns_record}")
    log.debug(f"Current time={time.time()} ttl_ts={ttl_ts}")
    if time.time() > ttl_ts:
        log.info(f"TTL expired for {name}")
        return None

    return (TYPE, name, value, ttl_ts, ttl)


def handle_client_message(udp_socket, msg, client_addr):
    if len(msg) == 4:
        name, value, record_type, ttl = pickle.loads(msg)
        initialize_auth_db()
        save_dns_record(name, value, ttl)
    elif len(msg) == 2:
        record_type, name = msg
        dns_record = get_dns_record(name)
        if dns_record:
            _, name, value, _, ttl = dns_record
            response = (record_type, name, value, ttl)
        else:
            response = ""
        response_bytes = pickle.dumps(response)
        udp_socket.sendto(response_bytes, client_addr)
    else:
        error_msg = f"Expected msg of len 4 or 2, got :{msg!r}"
        log.error(error_msg)
        udp_socket.sendto(error_msg.encode(), client_addr)


def main():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST_IP, SERVER_PORT))
    log.info(f"UDP server up and listening on {socket.gethostbyname(socket.gethostname())}:{SERVER_PORT}")

    while True:
        msg_bytes, client_addr = udp_socket.recvfrom(BUFFER_SIZE)
        msg = pickle.loads(msg_bytes)
        log.info(f"Message from Client: {msg!r}")
        handle_client_message(udp_socket, msg, client_addr)


if __name__ == '__main__':
    log.info("Spinning up authoritative server")
    main()

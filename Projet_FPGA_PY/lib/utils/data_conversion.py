import binascii

def bytes_to_hex(data_bytes):
    return binascii.hexlify(data_bytes).decode().upper()

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

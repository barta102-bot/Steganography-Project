import sys
from pathlib import Path
from Crypto.Cipher import AES
import hashlib
import random

ZWC = [
    '\u2060',  # 0
    '\u200b',  # 1
    '\u200d',  # 2
    '\u200e',  # 3
    '\u200f',  # 4
    '\u200c',  # 5
    '\u2061',  # 6
    '\u180e',  # 7
    '\u202a',  # 8
    '\u202c',  # 9
    '\u202d',  # a
    '\u2062',  # b
    '\u2063',  # c
    '\u2064',  # d
    '\u2065',  # e
    '\u2066',  # f
]

MARKER = '\ufeff'

def aes_encrypt(data_bytes, password):
    key = hashlib.sha256(password.encode()).digest() # converts password to 256 bit key
    cipher = AES.new(key, AES.MODE_EAX)

    ciphertext, tag = cipher.encrypt_and_digest(data_bytes) # encrypts data and generates tag

    return cipher.nonce + tag + ciphertext


def aes_decrypt(encrypted_bytes, password):
    key = hashlib.sha256(password.encode()).digest()

    nonce = encrypted_bytes[:16]
    tag = encrypted_bytes[16:32]
    ciphertext = encrypted_bytes[32:]

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    cipher.verify(tag)  # raises ValueError if wrong key
    return plaintext

# Hide secret file in cover file
def hide_message(secret_text, cover_text, position = "middle", key=None):
    # converts secret text into bytes
    data_bytes = secret_text.encode("utf-8")
    if key:
        data_bytes = aes_encrypt(data_bytes, key)
    # Convert secret to hex
    hex_msg = data_bytes.hex()

    # Encode hex using zero-width chars
    hidden = "".join(ZWC[int(ch, 16)] for ch in hex_msg)

    #Insert location
    if position == "front":
        payload = MARKER + hidden + MARKER
        return payload + cover_text
    elif position == "end":
        payload = MARKER + hidden + MARKER
        return cover_text + payload
    elif position == "random":
        return spread_hex(hidden, cover_text)
    else:
        payload = MARKER + hidden + MARKER
        mid = len(cover_text) // 2
        return cover_text[:mid] + payload + cover_text[mid:]


#Randomize where hex code is located for spread position
def spread_hex(hidden, cover_text):
    if len(cover_text) == 0:
        return hidden
    
    num_hex_chars = len(hidden)
    cover_len = len(cover_text)

    interval = cover_len // (num_hex_chars + 1)

    result = ""
    hex_indexing = 0

    for i, char in enumerate(cover_text):
        result += char

        if interval > 0 and (i + 1) % interval == 0 and hex_indexing < num_hex_chars:
            result += hidden[hex_indexing]
            hex_indexing += 1

    if hex_indexing < num_hex_chars:
        result += hidden[hex_indexing:]

    return result

# Reveal hidden file
def reveal_message(stego_text, key=None):

    parts = stego_text.split(MARKER)

    if len(parts) < 3:
        return None

    hidden = parts[1]

    hex_msg = ""

    for ch in hidden:
        if ch in ZWC:
            hex_msg += format(ZWC.index(ch), "x")

    try:
        data_bytes = bytes.fromhex(hex_msg)
        if key:
            data_bytes = aes_decrypt(data_bytes, key)

        return data_bytes.decode("utf-8")
    except:
        return None


# File Helpers
def read_file(path):
    return Path(path).read_text(encoding="utf-8")


def write_file(path, data):
    Path(path).write_text(data, encoding="utf-8")


# Main CLI
def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Hide  : steg.py hide secret.txt cover.txt output.txt [position] [key]")
        print("  Reveal: steg.py reveal stego.txt output.txt [key]")
        print(" Positions: Front, Middle (default), End, Random")
        sys.exit(1)

    mode = sys.argv[1].lower()

    # Hide Mode
    if mode == "hide":

        if len(sys.argv) < 5 or len(sys.argv) > 7:
            print("Usage: steg.py hide secret.txt cover.txt output.txt [position] [key]")
            sys.exit(1)

        secret_file = sys.argv[2]
        cover_file = sys.argv[3]
        output_file = sys.argv[4]
        position = sys.argv[5].lower() if len(sys.argv) >= 6 else "middle"
        key = sys.argv[6] if len(sys.argv) == 7 else None

        secret = read_file(secret_file)
        cover = read_file(cover_file)

        stego = hide_message(secret, cover, position, key)

        write_file(output_file, stego)

        print("✓ Message hidden successfully.")
        print(f"Output saved to: {output_file}")

    # Reveal Mode
    elif mode == "reveal":

        if len(sys.argv) < 4 or len(sys.argv) > 5:
            print("Usage: steg.py reveal stego.txt output.txt [key]")
            sys.exit(1)

        stego_file = sys.argv[2]
        output_file = sys.argv[3]
        key = sys.argv[4] if len(sys.argv) == 5 else None

        stego = read_file(stego_file)

        secret = reveal_message(stego, key)

        if secret is None:
            print("✗ No hidden message found.")
            sys.exit(1)

        write_file(output_file, secret)

        print("✓ Hidden message extracted.")
        print(f"Saved to: {output_file}")

    else:
        print("Invalid mode. Use 'hide' or 'reveal'.")
        sys.exit(1)


if __name__ == "__main__":
    main()

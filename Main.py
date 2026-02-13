import sys
from pathlib import Path
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


# Hide secret file in cover file
def hide_message(secret_text, cover_text, position = "middle"):

    # Convert secret to hex
    hex_msg = secret_text.encode("utf-8").hex()

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
def reveal_message(stego_text):

    parts = stego_text.split(MARKER)

    if len(parts) < 3:
        return None

    hidden = parts[1]

    hex_msg = ""

    for ch in hidden:
        if ch in ZWC:
            hex_msg += format(ZWC.index(ch), "x")

    try:
        return bytes.fromhex(hex_msg).decode("utf-8")
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
        print("  Hide  : steg.py hide secret.txt cover.txt output.txt position")
        print("  Reveal: steg.py reveal stego.txt output.txt")
        print(" Positions: Front, Middle (default), End, Random")
        sys.exit(1)

    mode = sys.argv[1].lower()

    # Hide Mode
    if mode == "hide":

        if len(sys.argv) < 5 or len(sys.argv) > 6:
            print("Usage: steg.py hide secret.txt cover.txt output.txt position")
            sys.exit(1)

        secret_file = sys.argv[2]
        cover_file = sys.argv[3]
        output_file = sys.argv[4]
        position = sys.argv[5].lower() if len(sys.argv) == 6 else "middle"

        secret = read_file(secret_file)
        cover = read_file(cover_file)

        stego = hide_message(secret, cover, position)

        write_file(output_file, stego)

        print("✓ Message hidden successfully.")
        print(f"Output saved to: {output_file}")

    # Reveal Mode
    elif mode == "reveal":

        if len(sys.argv) != 4:
            print("Usage: steg.py reveal stego.txt output.txt")
            sys.exit(1)

        stego_file = sys.argv[2]
        output_file = sys.argv[3]

        stego = read_file(stego_file)

        secret = reveal_message(stego)

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

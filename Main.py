import sys
from pathlib import Path

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
def hide_message(secret_text, cover_text):

    # Convert secret to hex
    hex_msg = secret_text.encode("utf-8").hex()

    # Encode hex using zero-width chars
    hidden = "".join(ZWC[int(ch, 16)] for ch in hex_msg)

    payload = MARKER + hidden + MARKER

    # Insert in middle of cover
    mid = len(cover_text) // 2

    return cover_text[:mid] + payload + cover_text[mid:]


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
        print("  Hide  : steg.py hide secret.txt cover.txt output.txt")
        print("  Reveal: steg.py reveal stego.txt output.txt")
        sys.exit(1)

    mode = sys.argv[1].lower()

    # Hide Mode
    if mode == "hide":

        if len(sys.argv) != 5:
            print("Usage: steg.py hide secret.txt cover.txt output.txt")
            sys.exit(1)

        secret_file = sys.argv[2]
        cover_file = sys.argv[3]
        output_file = sys.argv[4]

        secret = read_file(secret_file)
        cover = read_file(cover_file)

        stego = hide_message(secret, cover)

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

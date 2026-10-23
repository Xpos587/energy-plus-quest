from pathlib import Path
import struct
import zlib

root = Path(__file__).parent / 'selfcheck'
root.mkdir(exist_ok=True)
def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
def save(path, color):
    w = h = 32
    rows = b''.join(b'\x00' + bytes(color) * w for _ in range(h))
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')
    path.write_bytes(data)
save(root / 'style.png', (192, 96, 32))
save(root / 'source.png', (96, 96, 96))
save(root / 'target.png', (96, 96, 96))
print('created three 32x32 RGB PNG inputs')

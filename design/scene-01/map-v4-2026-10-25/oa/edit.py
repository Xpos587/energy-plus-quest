import base64, json, os, sys, time, urllib.request, uuid
img, out, size = sys.argv[1], sys.argv[2], sys.argv[3]
refs = sys.argv[4:]
prompt = open(os.path.join(os.path.dirname(__file__), "prompt.txt")).read()
b = uuid.uuid4().hex
parts = []
def field(n, v): parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
def file(n, p): parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{n}"; filename="{os.path.basename(p)}"\r\nContent-Type: image/png\r\n\r\n'.encode() + open(p, "rb").read() + b"\r\n")
field("model", os.environ.get("MODEL", "gpt-image-2")); field("prompt", prompt); field("size", size); field("quality", os.environ.get("Q", "high"))
for p in [img] + refs: file("image[]", p)
parts.append(f"--{b}--\r\n".encode())
req = urllib.request.Request("https://api.openai.com/v1/images/edits", data=b"".join(parts), headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": f"multipart/form-data; boundary={b}"})
t = time.time()
try:
    r = json.load(urllib.request.urlopen(req, timeout=900))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:800]); sys.exit(1)
open(out, "wb").write(base64.b64decode(r["data"][0]["b64_json"]))
print("OK", out, round(time.time() - t), "s", r.get("usage"))

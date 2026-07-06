#!/usr/bin/env python3
"""
Upload images to GitHub repository
Usage: python3 upload_images.py <GITHUB_TOKEN>
Get a token from: https://github.com/settings/tokens (scope: repo)
"""
import sys, os, base64, json, urllib.request

if len(sys.argv) < 2:
    print("Usage: python3 upload_images.py <GITHUB_TOKEN>")
    print("Get a token: https://github.com/settings/tokens -> New -> repo scope")
    sys.exit(1)

TOKEN = sys.argv[1]
OWNER, REPO, BRANCH = "WizLeery", "2026-Q2-WizLeery", "main"
API = "https://api.github.com"

def api_call(method, path, data=None):
    url = f"{API}/repos/{OWNER}/{REPO}{path}"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json", "User-Agent": "WizLeery-Portfolio"}
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  Error {e.code}: {e.read().decode()[:200]}")
        return None

print("Getting branch info...")
ref = api_call("GET", f"/git/ref/heads/{BRANCH}")
if not ref: print("Check your token."); sys.exit(1)
latest_sha = ref["object"]["sha"]
print(f"Current commit: {latest_sha[:8]}")

files = sorted([f for f in os.listdir("images") if f.endswith(".jpg")])
print(f"Uploading {len(files)} images...\n")

blobs = {}
for i, fname in enumerate(files):
    with open(f"images/{fname}", "rb") as f:
        content = base64.b64encode(f.read()).decode()
    print(f"[{i+1}/{len(files)}] {fname} ({len(content)/1024:.0f}KB)...", end=" ")
    blob = api_call("POST", "/git/blobs", {"content": content, "encoding": "base64"})
    if blob: blobs[f"images/{fname}"] = blob["sha"]; print(f"OK {blob['sha'][:8]}")
    else: print("FAILED")

if not blobs: print("No files uploaded."); sys.exit(1)

commit = api_call("GET", f"/git/commits/{latest_sha}")
tree = api_call("POST", "/git/trees", {"base_tree": commit["tree"]["sha"], "tree": [{"path": p, "mode": "100644", "type": "blob", "sha": s} for p, s in blobs.items()]})
new_commit = api_call("POST", "/git/commits", {"message": "Add portfolio images", "parents": [latest_sha], "tree": tree["sha"]})
api_call("PATCH", f"/git/refs/heads/{BRANCH}", {"sha": new_commit["sha"]})
print(f"\nDone! {len(blobs)} images uploaded to {OWNER}/{REPO}")
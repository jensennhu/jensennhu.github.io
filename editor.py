#!/usr/bin/env python3
"""
editor.py — Browser-based markdown editor for portfolio posts

Usage:
    python editor.py

Opens a live editor at http://localhost:5500 with:
  - Split-pane markdown editor + live preview
  - Drag & drop images (auto-saved to images/)
  - Publish button (commits and pushes to GitHub)
"""

import os
import sys
import json
import base64
import subprocess
import webbrowser
from datetime import date
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publish import (
    REPO_ROOT, POSTS_DIR, IMAGES_DIR, SITE_URL,
    slugify, get_toc_categories, update_toc,
)

PORT = 5500

# ---------------------------------------------------------------------------
# HTML / CSS / JS — embedded single-page app
# ---------------------------------------------------------------------------

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfolio Editor</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: #f6f8fa;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* ── Header ── */
  header {
    background: #24292f;
    color: #e6edf3;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }
  header svg { flex-shrink: 0; }
  header h1 { font-size: 15px; font-weight: 600; letter-spacing: 0.2px; }

  /* ── Toolbar ── */
  .toolbar {
    background: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 9px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
    flex-wrap: wrap;
  }
  .toolbar label {
    font-size: 12px;
    font-weight: 600;
    color: #57606a;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    white-space: nowrap;
  }
  .toolbar input[type="text"],
  .toolbar select {
    padding: 5px 10px;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    font-size: 13px;
    color: #24292f;
    background: #f6f8fa;
    outline: none;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .toolbar input[type="text"]:focus,
  .toolbar select:focus {
    border-color: #0969da;
    box-shadow: 0 0 0 3px rgba(9,105,218,0.15);
    background: #fff;
  }
  #title-input { flex: 1; min-width: 200px; max-width: 420px; }

  .spacer { flex: 1; }

  .publish-btn {
    background: #1a7f37;
    color: #fff;
    border: none;
    padding: 6px 18px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s;
    white-space: nowrap;
  }
  .publish-btn:hover:not(:disabled) { background: #156d30; }
  .publish-btn:disabled { background: #7cc896; cursor: not-allowed; }

  /* ── Panes ── */
  .panes {
    flex: 1;
    display: flex;
    overflow: hidden;
    min-height: 0;
  }

  .pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0;
  }
  .pane + .pane { border-left: 1px solid #d0d7de; }

  .pane-label {
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 600;
    color: #57606a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: #f6f8fa;
    border-bottom: 1px solid #d0d7de;
    flex-shrink: 0;
  }

  #editor {
    flex: 1;
    border: none;
    outline: none;
    padding: 16px;
    font-family: 'SFMono-Regular', 'Cascadia Code', Consolas, 'Liberation Mono', monospace;
    font-size: 13.5px;
    line-height: 1.65;
    resize: none;
    color: #24292f;
    background: #fff;
    tab-size: 2;
  }

  /* ── Preview typography ── */
  #preview {
    flex: 1;
    overflow-y: auto;
    padding: 18px 24px;
    background: #fff;
    font-size: 15px;
    line-height: 1.75;
    color: #24292f;
  }
  #preview img { max-width: 100%; border-radius: 6px; display: block; margin: 12px 0; }
  #preview h1, #preview h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 6px; margin: 1.4em 0 0.6em; }
  #preview h3, #preview h4 { margin: 1.2em 0 0.4em; }
  #preview p { margin: 0.75em 0; }
  #preview ul, #preview ol { padding-left: 2em; margin: 0.5em 0; }
  #preview li { margin: 0.25em 0; }
  #preview a { color: #0969da; }
  #preview code {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 12.5px;
    font-family: 'SFMono-Regular', Consolas, monospace;
  }
  #preview pre {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 14px 16px;
    overflow-x: auto;
    margin: 0.8em 0;
  }
  #preview pre code { background: none; border: none; padding: 0; }
  #preview blockquote {
    border-left: 3px solid #d0d7de;
    padding-left: 16px;
    color: #57606a;
    margin: 0.8em 0;
  }
  #preview strong { font-weight: 600; }
  #preview hr { border: none; border-top: 1px solid #d0d7de; margin: 1.5em 0; }
  #preview table { border-collapse: collapse; width: 100%; margin: 0.8em 0; }
  #preview th, #preview td { border: 1px solid #d0d7de; padding: 6px 12px; }
  #preview th { background: #f6f8fa; font-weight: 600; }

  /* ── Status bar ── */
  .statusbar {
    background: #24292f;
    color: #8b949e;
    padding: 4px 14px;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 7px;
    flex-shrink: 0;
  }
  .status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #3fb950;
    flex-shrink: 0;
    transition: background 0.2s;
  }
  .statusbar.busy .status-dot { background: #e3b341; }
  .statusbar.error .status-dot { background: #f85149; }
  .statusbar.success .status-dot { background: #3fb950; }
  #status-text { transition: color 0.2s; }
  .statusbar.error #status-text { color: #ffa198; }
  .statusbar.success #status-text { color: #56d364; }

  /* ── Drag overlay ── */
  #drag-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(9, 105, 218, 0.07);
    border: 3px dashed #0969da;
    z-index: 200;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 12px;
    pointer-events: none;
  }
  #drag-overlay.active { display: flex; }
  #drag-overlay span {
    font-size: 22px;
    font-weight: 700;
    color: #0969da;
    letter-spacing: -0.3px;
  }
  #drag-overlay small {
    font-size: 13px;
    color: #57606a;
  }
</style>
</head>
<body>

<header>
  <svg width="20" height="20" viewBox="0 0 16 16" fill="#e6edf3">
    <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zM9.5 3A1.5 1.5 0 0 1 8 1.5v-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4H9.5V3z"/>
  </svg>
  <h1>Portfolio Editor</h1>
</header>

<div class="toolbar">
  <label for="title-input">Title</label>
  <input type="text" id="title-input" placeholder="Post title…" autocomplete="off" />

  <label for="category-select">Category</label>
  <select id="category-select">
    <option value="">Loading…</option>
  </select>

  <div class="spacer"></div>
  <button class="publish-btn" id="publish-btn" onclick="publish()">Publish →</button>
</div>

<div class="panes">
  <div class="pane">
    <div class="pane-label">Markdown — drop images anywhere</div>
    <textarea id="editor" spellcheck="true" placeholder="Write your post in Markdown…&#10;&#10;Drop images onto this page to upload and insert them."></textarea>
  </div>
  <div class="pane">
    <div class="pane-label">Preview</div>
    <div id="preview"></div>
  </div>
</div>

<div class="statusbar" id="statusbar">
  <div class="status-dot"></div>
  <span id="status-text">Ready — drop images anywhere to upload</span>
</div>

<div id="drag-overlay">
  <span>Drop to upload image</span>
  <small>Image will be saved to images/ and inserted at cursor</small>
</div>

<script src="https://cdn.jsdelivr.net/npm/marked@9/marked.min.js"></script>
<script>
// ── Marked setup ────────────────────────────────────────────────────────────
marked.setOptions({ breaks: true, gfm: true });

// ── Elements ────────────────────────────────────────────────────────────────
const editor   = document.getElementById('editor');
const preview  = document.getElementById('preview');
const statusEl = document.getElementById('statusbar');
const statusTx = document.getElementById('status-text');
const overlay  = document.getElementById('drag-overlay');
const catSel   = document.getElementById('category-select');

// ── Live preview ─────────────────────────────────────────────────────────────
editor.addEventListener('input', updatePreview);
function updatePreview() {
  preview.innerHTML = marked.parse(editor.value || '');
}

// ── Status bar ───────────────────────────────────────────────────────────────
function setStatus(msg, state = 'idle') {
  // state: 'idle' | 'busy' | 'error' | 'success'
  statusEl.className = 'statusbar ' + state;
  statusTx.textContent = msg;
}

// ── Categories ───────────────────────────────────────────────────────────────
async function loadCategories() {
  try {
    const cats = await fetch('/categories').then(r => r.json());
    catSel.innerHTML = '';
    cats.forEach(cat => {
      const o = document.createElement('option');
      o.value = cat; o.textContent = cat;
      catSel.appendChild(o);
    });
    const newOpt = document.createElement('option');
    newOpt.value = '__new__'; newOpt.textContent = '＋ New category';
    catSel.appendChild(newOpt);
  } catch {
    setStatus('Could not load categories — is the server running?', 'error');
  }
}

catSel.addEventListener('change', () => {
  if (catSel.value !== '__new__') return;
  const name = prompt('Enter new category name:');
  if (name && name.trim()) {
    const opt = document.createElement('option');
    opt.value = name.trim();
    opt.textContent = name.trim();
    catSel.insertBefore(opt, catSel.querySelector('option[value="__new__"]'));
    catSel.value = name.trim();
  } else {
    catSel.selectedIndex = 0;
  }
});

// ── Drag & drop ───────────────────────────────────────────────────────────────
let dragDepth = 0;

document.addEventListener('dragenter', e => {
  if ([...e.dataTransfer.types].includes('Files')) {
    dragDepth++;
    overlay.classList.add('active');
  }
});
document.addEventListener('dragleave', () => {
  if (--dragDepth <= 0) { dragDepth = 0; overlay.classList.remove('active'); }
});
document.addEventListener('dragover', e => e.preventDefault());
document.addEventListener('drop', async e => {
  e.preventDefault();
  dragDepth = 0;
  overlay.classList.remove('active');
  const images = [...e.dataTransfer.files].filter(f => f.type.startsWith('image/'));
  if (!images.length) { setStatus('Drop ignored — only image files are supported', 'error'); return; }
  for (const img of images) await uploadImage(img);
});

// ── Image upload ──────────────────────────────────────────────────────────────
async function uploadImage(file) {
  setStatus(`Uploading ${file.name}…`, 'busy');
  const b64 = await new Promise(res => {
    const r = new FileReader();
    r.onload = () => res(r.result.split(',')[1]);
    r.readAsDataURL(file);
  });
  try {
    const data = await fetch('/upload-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: file.name, data: b64 }),
    }).then(r => r.json());
    if (data.error) { setStatus(`Upload failed: ${data.error}`, 'error'); return; }
    insertAtCursor('\n' + data.markdown + '\n');
    setStatus(`Uploaded ${data.filename} — inserted into editor`, 'success');
  } catch (err) {
    setStatus(`Upload error: ${err.message}`, 'error');
  }
}

function insertAtCursor(text) {
  const s = editor.selectionStart, e2 = editor.selectionEnd;
  editor.value = editor.value.slice(0, s) + text + editor.value.slice(e2);
  editor.selectionStart = editor.selectionEnd = s + text.length;
  editor.focus();
  updatePreview();
}

// ── Publish ───────────────────────────────────────────────────────────────────
async function publish() {
  const title    = document.getElementById('title-input').value.trim();
  const category = catSel.value;
  const content  = editor.value.trim();

  if (!title)    { setStatus('Title is required before publishing', 'error'); return; }
  if (!category) { setStatus('Category is required before publishing', 'error'); return; }
  if (!content)  { setStatus('Post content is empty', 'error'); return; }

  const btn = document.getElementById('publish-btn');
  btn.disabled = true;
  setStatus('Publishing… committing and pushing to GitHub', 'busy');

  try {
    const res = await fetch('/publish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, category, content }),
    }).then(r => r.json());

    if (res.error) {
      setStatus(`Publish failed: ${res.error}`, 'error');
    } else {
      setStatus(`Published! Live at: ${res.url}  (GitHub Actions takes ~1 min to build)`, 'success');
    }
  } catch (err) {
    setStatus(`Network error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
  }
}

// ── Init ─────────────────────────────────────────────────────────────────────
loadCategories();
updatePreview();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# HTTP request handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            self._html()
        elif path == '/categories':
            self._json(get_toc_categories())
        elif path.startswith('/images/'):
            self._image(path[len('/images/'):])
        else:
            self._json({'error': 'Not found'}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/upload-image':
            self._upload_image()
        elif path == '/publish':
            self._publish()
        else:
            self._json({'error': 'Not found'}, 404)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _body(self):
        n = int(self.headers.get('Content-Length', 0))
        return json.loads(self.rfile.read(n))

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _html(self):
        body = HTML.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _image(self, filename):
        img_path = os.path.join(IMAGES_DIR, os.path.basename(filename))
        if not os.path.isfile(img_path):
            self._json({'error': 'Not found'}, 404)
            return
        ext = os.path.splitext(filename)[1].lstrip('.').lower()
        mime = {
            'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'gif': 'image/gif', 'webp': 'image/webp', 'svg': 'image/svg+xml',
        }.get(ext, 'application/octet-stream')
        with open(img_path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    # ── POST /upload-image ────────────────────────────────────────────────────

    def _upload_image(self):
        body = self._body()
        filename = os.path.basename(body['filename'])
        data = base64.b64decode(body['data'])

        dest = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(dest):
            base, ext = os.path.splitext(filename)
            i = 1
            while os.path.exists(dest):
                filename = f"{base}_{i}{ext}"
                dest = os.path.join(IMAGES_DIR, filename)
                i += 1

        with open(dest, 'wb') as f:
            f.write(data)

        alt = os.path.splitext(filename)[0]
        self._json({'filename': filename, 'markdown': f'![{alt}](/images/{filename})'})

    # ── POST /publish ─────────────────────────────────────────────────────────

    def _publish(self):
        body = self._body()
        title    = body.get('title', '').strip()
        content  = body.get('content', '').strip()
        category = body.get('category', '').strip()

        if not title:
            self._json({'error': 'Title is required'}, 400); return
        if not content:
            self._json({'error': 'Content is empty'}, 400); return
        if not category:
            self._json({'error': 'Category is required'}, 400); return

        slug     = slugify(title)
        today    = date.today()
        filename = f"{today.strftime('%Y-%m-%d')}-{slug}.md"
        dest     = os.path.join(POSTS_DIR, filename)

        if os.path.exists(dest):
            self._json({'error': f'Post already exists: _posts/{filename}'}, 409); return

        full = f"---\nlayout: post\ntitle: {title}\n---\n\n{content}\n"
        with open(dest, 'w') as f:
            f.write(full)

        url = f"{SITE_URL}/{today.strftime('%Y/%m/%d')}/{slug}/"
        update_toc(title, url, category)

        try:
            subprocess.run(['git', 'add', '_posts/', 'images/'], cwd=REPO_ROOT, check=True)
            subprocess.run(['git', 'commit', '-m', f'Add post: {title}'], cwd=REPO_ROOT, check=True)
            subprocess.run(['git', 'push'], cwd=REPO_ROOT, check=True)
        except subprocess.CalledProcessError as e:
            self._json({'error': str(e), 'url': url}, 500); return

        self._json({'url': url})

    def log_message(self, *_):
        pass  # suppress console noise


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), Handler)
    url = f'http://localhost:{PORT}'
    print(f'Portfolio editor → {url}')
    print('Press Ctrl+C to stop.\n')
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')

import os, json
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path('configs/.env')
    if env_path.exists():
        load_dotenv(env_path)
except Exception:
    pass

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not url or not key:
    print(json.dumps({'ok': False, 'error': 'SUPABASE_URL ou SUPABASE_KEY ausentes no ambiente'}))
    raise SystemExit(0)

try:
    from supabase import create_client
    supa = create_client(url, key)
    res = supa.table('embeddings').select('id,metadata').limit(5).execute()
    data = res.data if isinstance(res.data, list) else []
    # Evitar vazar metadados sensíveis: truncar campos muito longos
    sanitized = []
    for row in data:
        md = row.get('metadata') or {}
        if isinstance(md, dict):
            # Truncar textos longos
            md = {k: (v[:200] + '…' if isinstance(v, str) and len(v) > 200 else v) for k, v in md.items()}
        sanitized.append({'id': row.get('id'), 'metadata': md})
    print(json.dumps({'ok': True, 'count': len(sanitized), 'rows': sanitized}, ensure_ascii=False))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))

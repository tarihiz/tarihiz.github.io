"""Öğretmen için çevrimdışı katılım kodu ve Supabase CSV içe aktarma dosyası."""
import csv, os, secrets, hashlib, hmac, argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--count',type=int,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
pepper=os.environ.get('CODE_PEPPER','')
if len(pepper)<32:raise SystemExit('Sunucuyla aynı, en az 32 karakterlik CODE_PEPPER gerekli.')
if not 1<=args.count<=1000:raise SystemExit('Adet 1–1000 olmalı.')
args.out.mkdir(parents=True,exist_ok=True)
with (args.out/'ogretmen_kodlari.csv').open('x',newline='') as raw,(args.out/'supabase_katilimcilar.csv').open('x',newline='') as hashed:
 a=csv.writer(raw);b=csv.writer(hashed);a.writerow(['label','code']);b.writerow(['label','code_hash'])
 for i in range(args.count):
  code=secrets.token_urlsafe(12);label=f'Ogrenci-{i+1:03}'
  a.writerow([label,code]);b.writerow([label,hmac.new(pepper.encode(),code.encode(),hashlib.sha256).hexdigest()])
print('İki CSV oluşturuldu. Ham kodları yalnız öğretmen saklamalı; GitHub’a eklemeyin.')

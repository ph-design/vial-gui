import json, sys, os
base = os.path.dirname(os.path.dirname(__file__))
# qmk_settings.json lives in src/main/resources/base
qs_path = os.path.join(os.path.dirname(base), 'resources', 'base', 'qmk_settings.json')
qs = json.load(open(qs_path, 'r', encoding='utf-8'))
texts = set()
for tab in qs.get('tabs', []):
    texts.add(tab.get('name',''))
    for f in tab.get('fields',[]):
        texts.add(f.get('title',''))

sys.path.insert(0, base)
import i18n
translations = i18n.I18n._translations.get('zh_CN', {})
missing = [t for t in sorted(texts) if t and t not in translations]
print('Total strings in qmk_settings.json:', len(texts))
print('Missing translations:', len(missing))
for m in missing:
    print(repr(m))

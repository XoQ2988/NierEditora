import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict

from nier_editora.core.constants import ITEM_LIST

_I18N_DIR = Path(__file__).parent.parent / "data" / "i18n"


@lru_cache(maxsize=4)
def load_translations(lang: str) -> Dict[str, str]:
    path = os.path.join(_I18N_DIR, f"{lang}.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

_current_lang = "en"
_trans = load_translations(_current_lang)


def set_language(lang: str):
    global _current_lang, _trans
    _current_lang = lang
    _trans = load_translations(lang)

def translate_item(item_id: int) -> str:
    return _trans.get(str(f"{item_id}:" + (ITEM_LIST.get(item_id) or "???")))


def dumpTranslationSkeleton(lang: str = "en") -> Path:
    _I18N_DIR.mkdir(exist_ok=True)
    out_path = _I18N_DIR / f"{lang}.json"
    skeleton = {str(item_id): code for item_id, code in ITEM_LIST.items()}
    json_text = json.dumps(skeleton, ensure_ascii=False, indent=2)
    out_path.write_text(json_text, encoding="utf-8")
    return out_path

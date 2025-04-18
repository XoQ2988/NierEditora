import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict

from nier_editora.core.constants import ITEM_LIST
from nier_editora.core.exceptions import TranslationError

logger = logging.getLogger(__name__)

# Directory where translation JSON files are stored
_I18N_DIR = Path(__file__).parent.parent / "data" / "i18n"

@lru_cache(maxsize=4)
def load_translations(lang: str) -> Dict[str, str]:
    """
    Load translations for a given language code from a JSON file.

    Args:
        lang: Language code (e.g., "en", "ja").

    Returns:
        A dict mapping item keys to translated names.

    Raises:
        TranslationError: If JSON parsing fails or file is unreadable.
    """
    path = _I18N_DIR / f"{lang}.json"
    if not path.exists():
        logger.warning(f"Translation file not found for '{lang}': {path}")
        return {}
    try:
        logger.debug(f"Loading translations from {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        logger.info(f"Loaded {len(data)} translations for '{lang}'")
        return data
    except Exception as e:
        logger.error(f"Failed to load translations for '{lang}': {e}")
        raise TranslationError(f"Error loading translations for '{lang}': {e}")

# Current in-memory translation mapping
_current_lang: str = "en"
_translations: Dict[str, str] = load_translations(_current_lang)


def set_language(lang: str) -> None:
    """
    Set the application language for translations.

    Args:
        lang: New language code to use.
    """
    global _current_lang, _translations
    _current_lang = lang
    _translations = load_translations(lang)
    logger.info(f"Language set to '{lang}' with {_translations.__len__()} entries")


def translate_item(item_id: int) -> str:
    """
    Translate an item ID to its localized name.

    Args:
        item_id: Numeric item identifier.

    Returns:
        The translated item name if available, otherwise the default code.

    Raises:
        TranslationError: If translations for current language haven't been loaded.
    """
    if not _translations:
        logger.debug("No translations loaded; defaulting to ITEM_LIST values")
    key = str(item_id)
    default = ITEM_LIST.get(item_id, "UNKNOWN")
    trans_key = f"{key}:{default}"
    # Return translated name or fallback default
    return _translations.get(trans_key, default)


def dump_translation_skeleton(lang: str = "en") -> Path:
    """
    Generate a JSON skeleton file for translations based on ITEM_LIST keys.

    Args:
        lang: Language code for the skeleton file.

    Returns:
        Path to the created skeleton JSON file.
    """
    _I18N_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _I18N_DIR / f"{lang}.json"
    skeleton = {str(item_id): code for item_id, code in ITEM_LIST.items()}
    content = json.dumps(skeleton, ensure_ascii=False, indent=2)
    out_path.write_text(content, encoding="utf-8")
    logger.info(f"Created translation skeleton at {out_path}")
    return out_path

import argparse
import logging
import sys
from pathlib import Path

from .logging_config import setup_logging
from .core.save import SaveFile
from utils import console_to_pc, pc_to_console

logger = logging.getLogger(__name__)

def cmd_info(args: argparse.Namespace) -> None:
    """
    Show core save metadata: player name, play time, money, and XP.

    Args:
        args: Parsed command-line arguments (expects args.file to be Path).
    """
    logger.debug("Executing 'info' with file=%s", args.file)
    save = SaveFile.load_from_file(args.file)
    hours, rem = divmod(save.play_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Player Name : {save.player_name}")
    print(f"Play Time   : {hours:02d}:{minutes:02d}:{seconds:02d}")
    print(f"Money       : {save.money}")
    print(f"XP          : {save.xp}")
    logger.info("Displayed metadata for %s", args.file)

def cmd_set(args: argparse.Namespace) -> None:
    """
    Modify one or more fields in the save file.

    Args:
        args: Parsed CLI args with optional fields to set (name, time, money, xp).
    """
    logger.debug("Executing 'set' with args=%s", args)
    save = SaveFile.load_from_file(args.file)
    updated = False

    if args.name is not None:
        save.player_name = args.name[:35]
        print(f"  ↳ name = {save.player_name}")
        logger.info("Player name set to %s", save.player_name)
        updated = True

    if args.time is not None:
        try:
            h, m, s = map(int, args.time.split(':'))
            save.play_time = h * 3600 + m * 60 + s
            print(f"  ↳ play_time = {args.time}")
            logger.info("Play time set to %s", args.time)
            updated = True
        except ValueError:
            logger.error("Invalid time format '%s'; use HH:MM:SS", args.time)
            sys.exit(1)

    if args.money is not None:
        if args.money < 0:
            logger.error("Money must be non-negative, got %d", args.money)
            sys.exit(1)
        save.money = args.money
        print(f"  ↳ money = {save.money}")
        logger.info("Money set to %d", save.money)
        updated = True

    if args.xp is not None:
        if args.xp < 0:
            logger.error("XP must be non-negative, got %d", args.xp)
            sys.exit(1)
        save.xp = args.xp
        print(f"  ↳ xp = {save.xp}")
        logger.info("XP set to %d", save.xp)
        updated = True

    if not updated:
        logger.error("No fields specified to set")
        sys.exit(1)

    destination = args.output or args.file
    save.save_to_file(destination)
    logger.info("Saved updated save to %s", destination)
    print(f"Saved to {destination}")

def cmd_convert(args: argparse.Namespace) -> None:
    """
    Convert between PC and console save file formats.

    Args:
        args: CLI args (expects args.file as Path and a --to-pc or --to-console flag).
    """
    logger.debug("Executing 'convert' with args=%s", args)
    data = args.file.read_bytes()
    try:
        if args.to_pc:
            out_data = console_to_pc(data)
            direction = 'Console → PC'
        else:
            out_data = pc_to_console(data)
            direction = 'PC → Console'
        logger.info("Conversion %s successful for %s", direction, args.file)
    except Exception as e:
        logger.exception("Conversion failed for %s", args.file)
        sys.exit(1)

    destination = args.output or args.file
    destination.write_bytes(out_data)
    print(f"Converted ({direction}) and wrote to {destination}")

def main() -> int:
    """
    Entry point for the NierEditora CLI.

    Parses command-line arguments, configures logging, and dispatches subcommands.

    Returns:
        Exit code: 0 on success, non-zero on error.
    """
    parser = argparse.ArgumentParser(
        prog="niereditora",
        description="NierEditora - NieR:Automata Save Editor CLI"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress INFO messages; only show warnings and errors."
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # info subcommand
    p_info = subparsers.add_parser("info", help="Show core save metadata")
    p_info.add_argument("file", type=Path, help="Path to save file")
    p_info.set_defaults(func=cmd_info)

    # set subcommand
    p_set = subparsers.add_parser("set", help="Modify one or more player fields")
    p_set.add_argument("file", type=Path, help="Path to save file")
    p_set.add_argument("-o", "--output", type=Path,
                       help="Write result to this path (default: overwrite input)")
    p_set.add_argument("--name", type=str, help="Player name (max 35 chars)")
    p_set.add_argument("--time", type=str, help="Play time as HH:MM:SS")
    p_set.add_argument("--money", type=int, help="Money (non-negative integer)")
    p_set.add_argument("--xp", type=int, help="XP (non-negative integer)")
    p_set.set_defaults(func=cmd_set)

    # convert subcommand
    p_conv = subparsers.add_parser("convert", help="Convert between PC and console formats")
    p_conv.add_argument("file", type=Path, help="Path to save file")
    p_conv.add_argument("-o", "--output", type=Path,
                        help="Write converted file here (default: overwrite input)")
    group = p_conv.add_mutually_exclusive_group(required=True)
    group.add_argument("--to-pc", action="store_true",
                       help="Convert console save → PC format")
    group.add_argument("--to-console", action="store_true",
                       help="Convert PC save → console format")
    p_conv.set_defaults(func=cmd_convert)

    args = parser.parse_args()

    # Configure logging
    level = "WARNING" if args.quiet else "DEBUG"
    setup_logging(level=level)

    try:
        args.func(args)
    except SystemExit:
        raise
    except Exception:
        logger.exception("An unexpected error occurred")
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
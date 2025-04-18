import argparse
import logging
import sys
from pathlib import Path

from nier_editora.core.save import SaveFile
from utils import console_to_pc, pc_to_console

LOG = logging.getLogger(__name__)


def cmd_info(args):
    save = SaveFile.load_from_file(args.file)
    h, r = divmod(save.play_time, 3600)
    m, s = divmod(r, 60)
    print(f"Player Name : {save.player_name}")
    print(f"Play Time   : {h:02d}:{m:02d}:{s:02d}")
    print(f"Money       : {save.money}")
    print(f"XP          : {save.xp}")

def cmd_set(args):
    save = SaveFile.load_from_file(args.file)
    updated = False

    if args.name is not None:
        save.player_name = args.name[:35]
        print(f"  ↳ name = {save.player_name}")
        updated = True

    if args.time is not None:
        try:
            h, m, s = (int(x) for x in args.time.split(":"))
            save.play_time = h*3600 + m*60 + s
            print(f"  ↳ play_time = {args.time}")
            updated = True
        except Exception:
            LOG.error("Invalid time format; use HH:MM:SS")
            sys.exit(1)

    if args.money is not None:
        if args.money < 0:
            LOG.error("Money must be non-negative")
            sys.exit(1)
        save.money = args.money
        print(f"  ↳ money = {save.money}")
        updated = True

    if args.xp is not None:
        if args.xp < 0:
            LOG.error("XP must be non-negative")
            sys.exit(1)
        save.xp = args.xp
        print(f"  ↳ xp = {save.xp}")
        updated = True

    if not updated:
        LOG.error("No fields specified to set.")
        sys.exit(1)

    out = args.output or args.file
    save.save_to_file(out)
    print(f"Saved to {out}")

def cmd_convert(args):
    data = args.file.read_bytes()
    try:
        if args.to_pc:
            out_data = console_to_pc(data)
        else:
            out_data = pc_to_console(data)
    except Exception as e:
        LOG.error("Conversion failed: %s", e)
        sys.exit(1)

    out_path = args.output or args.file
    out_path.write_bytes(out_data)
    mode = "Console to Pc" if args.to_pc else "Pc to Console"
    print(f"Converted ({mode}) and wrote to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="niereditora",
        description="NierEditora - NieR:Automata Save Editor CLI"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="suppress INFO messages"
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # info
    p = sub.add_parser("info", help="Show core save metadata")
    p.add_argument("file", type=Path, help="Path to save file")
    p.set_defaults(func=cmd_info)

    # set
    p = sub.add_parser("set", help="Modify one or more player fields")
    p.add_argument("file", type=Path, help="Path to save file")
    p.add_argument("-o", "--output", type=Path,
                   help="Write result to this path (default: overwrite)")
    p.add_argument("--name", type=str, help="Player name (max 35 chars)")
    p.add_argument("--time", type=str, help="Play time as HH:MM:SS")
    p.add_argument("--money", type=int, help="Money (non-negative integer)")
    p.add_argument("--xp", type=int, help="XP (non-negative integer)")
    p.set_defaults(func=cmd_set)

    # convert
    p = sub.add_parser("convert", help="Convert between PC and console formats")
    p.add_argument("file", type=Path, help="Path to save file")
    p.add_argument("-o", "--output", type=Path,
                   help="Write converted file here (default: overwrite input)")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--to-pc", action="store_true",
                       help="Convert console save -> PC format")
    group.add_argument("--to-console", action="store_true",
                       help="Convert PC save -> console format")
    p.set_defaults(func=cmd_convert)

    args = parser.parse_args()
    args.func(args)

    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        level=level
    )


if __name__ == '__main__':
    main()

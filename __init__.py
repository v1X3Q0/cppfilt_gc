from binaryninja.binaryview import BinaryViewType, BinaryView, Endianness
from binaryninja.interaction import get_directory_name_input, get_text_line_input, get_open_filename_input
from binaryninja.log import log_alert, log_error, log_info, log_warn
from binaryninja import PluginCommand
from .cppfilt_gc import cppfilt_gc
import argparse
import re
import os
import json

def cppfilt_gc_all(bv: BinaryView):
    funcdict={}
    arglist="pseudo c args\n" \
        "--apply file to open and apply to the running binaryview\n" \
        "--save file to save from what the running bv has\n" \
        "--now apply the cppfilt stuff now\n" \
        "--print print each entry\n"
    args = get_text_line_input(arglist, "cppfilt_gc argument list")
    argparser = argparse.ArgumentParser('cppfilt_gc')
    argparser.add_argument('--apply', '-a', action='store_true', help="file to open, read, and apply to the current bv")
    argparser.add_argument("--save", "-s", help="file to save contents to")
    argparser.add_argument("--now", "-n", action="store_true", help="apply the translations now")
    argparser.add_argument('--print', '-p', action='store_true', help='dump results to screen')

    if args != None:
        args = args.decode("utf-8")
    else:
        return
    args = re.sub(r"[ ]+", " ", args)
    args = argparser.parse_args(str(args).split(' '))

    if args.apply == True:
        applyfile = get_open_filename_input('json file with dictionary of routines')
        if os.path.exists(applyfile):
            with open(applyfile, "r") as statfile:
                crashdict = json.loads(statfile.read())
                for address in crashdict.keys():
                    address_int = int(address)
                    func = bv.get_function_at(address_int)
                    func.name = crashdict[address]['new']
        else:
            log_error(f'json file {applyfile} does not exitsts')
            return
        print(f"loaded file {applyfile}")
        return

    for func in bv.functions:
        try:
            namedeobf = cppfilt_gc(func.name)
        except:
            log_error(f'failed on {func.name}')
            break
        if namedeobf == None:
            continue
        funcdict[func.start] = {}
        funcdict[func.start]['orig'] = func.name
        funcdict[func.start]['new'] = namedeobf
        if args.print == True:
            print(func.name, namedeobf)
        if args.now == True:
            func.name = namedeobf
    if args.save != None:
        try:
            with open(args.save, "w") as statfile:
                json.dump(funcdict, statfile)
        except:
            log_error(f'json file {args.save} can not exitsts')
            return
        print(f"saved file {args.save}")
    return

PluginCommand.register("cppfilt_gc", "cleanup gamecube obfuscated c++ names", cppfilt_gc_all)
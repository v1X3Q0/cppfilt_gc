from binaryninja.binaryview import BinaryViewType, BinaryView, Endianness
from binaryninja.interaction import get_directory_name_input, get_text_line_input
from binaryninja import PluginCommand
from .cppfilt_gc import cppfilt_gc

def cppfilt_gc_all(bv: BinaryView):
    args = get_text_line_input("cppfilt_gc argument list", "args")
    args = '/Users/mariomain/Documents/meme.txt'
    f = open(args, 'w')
    for func in bv.functions:
        try:
            namedeobf = cppfilt_gc(func.name)
            print(func.name, namedeobf)
            # if namedeobf == '()':
            #     print(f'failed on {func.name}')
            #     break
        except:
            print(f'failed on {func.name}')
            break
        f.write(f'{func.name}, {namedeobf}\n')
    f.close()
    return

PluginCommand.register("cppfilt_gc", "cleanup gamecube obfuscated c++ names", cppfilt_gc_all)
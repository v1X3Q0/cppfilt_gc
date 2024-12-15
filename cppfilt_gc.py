
import re
import argparse

def templatestring(classname):
    classnameraw = re.match(r'([a-zA-Z_][a-zA-Z0-9_]+)', classname)
    classnameraw = classnameraw.group(1)
    if classnameraw != classname:
        templates = re.search(r'\<([a-zA-Z0-9_][a-zA-Z0-9_,]*)\>', classname)
        templates = templates.group(1).split(',')
        templates_fixed = []
        for template in templates:
            templates_fixed += fieldsparsing(template)
        classname = classnameraw + '<' + ','.join(templates_fixed) + '>'
    return classname

def namespaceprepend(fieldstr, classname):
    namespaceclass=classname
    if str(fieldstr[0]).isnumeric():
        namespaceclass = re.match(r'([0-9]+)([a-zA-Z_][a-zA-Z0-9_<>,]+)', fieldstr)
        namespaceclass_len = int(namespaceclass.group(1))
        fieldstr = namespaceclass.group(2)[namespaceclass_len:]
        namespaceclass = namespaceclass.group(2)[0:namespaceclass_len]
    return fieldstr, namespaceclass

def outfuncformat(name_func, arglist):
    out_str = None
    if name_func != '':
        out_str = ''
        out_str += name_func
        out_str += '('
        if len(arglist) > 0:
            for i in range(0, len(arglist) - 1):
                out_str += arglist[i] + ', '
            out_str += arglist[len(arglist) - 1]
        out_str += ')'
        # print(out_str)
    return out_str

def fieldtype(typestr: str, classtype=False, classptr=True):
    arglist = []
    clsptr = '*'
    # print(typestr)

    if classptr == False:
        clsptr = ''
    
    # characters are lcefib
    if classtype == False:
        if typestr == 'Fv':
            arglist = arglist
        elif typestr == 'Rf':
            arglist.append('float*')
        elif typestr == 'Pv_v':
            arglist.append('void (*)()')
        else:
            for typeparm in typestr:
                if typeparm == 'b':
                    arglist.append('char')
                elif typeparm == 'i':
                    arglist.append('int')
                elif typeparm == 'l':
                    arglist.append('long')
                elif typeparm == 'c':
                    arglist.append('char*')
                elif typeparm == 's':
                    arglist.append('const char*')
                elif typeparm == 'f':
                    arglist.append('double')
                elif typeparm == 'v':
                    arglist.append('void*')
    elif classtype == True:
        if typestr != '':
            arglist.append(f'{typestr}{clsptr}')
    return arglist

def fieldsparsing(fieldstr: str):
    arglist = []
    curField=''
    tilnextarg=0
    for i in range(0, len(fieldstr)):
        curchar = fieldstr[i]
        if tilnextarg > 0:
            tilnextarg -= 1
        else:
            if str(curchar).isupper() == True:
                arglist += fieldtype(curField)
                curField = curchar
            # class field
            elif str(curchar).isnumeric() == True:
                classp = False
                arglist += fieldtype(curField)
                if (i > 0) and (fieldstr[i - 1] == 'P'):
                    classp = True
                # this is the literal class name
                paramcur = re.match(r'([0-9]+)([a-zA-Z_][a-zA-Z0-9_]*)', fieldstr[i:])
                if paramcur == None:
                    # but it seems like it can be an immediate?
                    paramcur = re.match(r'([0-9]+)', fieldstr[i:])
                    paramcurlen = 0
                else:
                    paramcurlen = int(paramcur.group(1))
                    paramcurname = paramcur.group(2)[0:paramcurlen]
                    arglist += fieldtype(paramcurname, True, classp)
                tilnextarg = (len(paramcur.group(1)) + paramcurlen) - 1
            else:
                curField += curchar
    else:
        arglist += fieldtype(curField)
    return arglist

def cppfilt_gc(name: str):
    unscoped_func = re.match(r'([a-zA-Z_][a-zA-Z0-9_<>,]*)__(F[a-zA-Z_0-9]+)', name)
    class_func = re.match(r'([a-zA-Z_][a-zA-Z0-9_<>,]*)__(Q2)?([0-9]+)([a-zA-Z_][a-zA-Z0-9_<>,]+)', name)
    ctr_func = re.match(r'__([a-z]{2,3})__(Q2)?([a-zA-Z0-9_<>,]+)', name)
    cast_func = re.match(r'__op([a-zA-Z]+)__(Q2)?([a-zA-Z0-9_<>,]+)', name)
    arglist = []
    name_func = ''
    fieldstr = namespacename = classname = classnamenet = ''
    # __opPCc__6StringCFv
    if cast_func != None:
        fieldstr = cast_func.group(1)
        rettype=fieldsparsing(fieldstr)
        rettype = rettype[0]
        if '*' in rettype:
            rettype = rettype.replace('*', '_ptr')
        if cast_func.group(3)[0].isnumeric() == True:
            cast_func = re.match(r'__([a-zA-Z]+)__(Q2)?([0-9]+)([a-zA-Z_][a-zA-Z0-9_<>,]+)', name)
            classname_len = int(cast_func.group(3))
            classname = cast_func.group(4)[0:classname_len]
            classname = templatestring(classname)
            fieldstr = cast_func.group(4)[classname_len:]
            classnamenet = namespacename = classname
            fieldstr, classname = namespaceprepend(fieldstr, classname)
        else:
            fieldstr = cast_func.group(3)
        if namespacename != classname:
            classnamenet = namespacename + '::' + classname
        name_func = classnamenet + '::cast_' + rettype        
    # __ct__17ZeroParticleCacheFP9ZeroVideoPCc19ZeroRenderBlendMode
    elif (ctr_func != None):
        # these seem to be pure, or empty
        if ctr_func.group(3)[0].isnumeric() == True:
            ctr_func = re.match(r'__([a-z]{2,3})__(Q2)?([0-9]+)([a-zA-Z_][a-zA-Z0-9_<>,]+)', name)
            classname_len = int(ctr_func.group(3))
            classname = ctr_func.group(4)[0:classname_len]
            classname = templatestring(classname)
            fieldstr = ctr_func.group(4)[classname_len:]
            classnamenet = namespacename = classname
            fieldstr, classname = namespaceprepend(fieldstr, classname)
        else:
            fieldstr = ctr_func.group(3)
        if namespacename != classname:
            classnamenet = namespacename + '::' + classname
        if ctr_func.group(1) == 'ct':
            name_func = classnamenet + "::" + classname
        elif ctr_func.group(1) == 'dt':
            name_func = classnamenet + "::~" + classname
        elif ctr_func.group(1) == 'dl':
            if classnamenet != '':
                name_func = classnamenet + "::operator delete"
            else:
                name_func = "operator delete"
        elif ctr_func.group(1) == 'dla':
            name_func = "operator delete"
        elif ctr_func.group(1) == 'nw':
            if classnamenet != '':
                name_func = classnamenet + "::operator new"
            else:
                name_func = "operator new"
        elif ctr_func.group(1) == 'nwa':
            name_func = "operator new"
        elif ctr_func.group(1) == 'pl':
            name_func = "std::copy"
        elif ctr_func.group(1) == 'apl':
            name_func = "std::move"
        elif ctr_func.group(1) == 'pp':
            name_func = classnamenet
        # technically the q2 functions seem to be pure, but we don't have to care
        # about those. if we do, we act on the group1
        # if ctr_func.group(1) != None:
        arglist += fieldtype(classnamenet, True)
        arglist += fieldsparsing(fieldstr)
    # ZFree__FPvPv
    elif unscoped_func != None:
        name_func = unscoped_func.group(1)
        fieldstr = unscoped_func.group(2)
        name_func = templatestring(name_func)
        fieldstr, namespacename = namespaceprepend(fieldstr, "")
        if namespacename != '':
            name_func = namespacename + '::' + name_func
        arglist += fieldsparsing(fieldstr)
    # PostLoad__9VMHandlerFv
    elif class_func != None:
        name_func = class_func.group(1)
        classname_len = int(class_func.group(3))
        classname = class_func.group(4)[0:classname_len]
        classname = templatestring(classname)
        fieldstr = class_func.group(4)[classname_len:]
        classnamenet = namespacename = classname
        fieldstr, classname = namespaceprepend(fieldstr, classname)
        if namespacename != classname:
            classnamenet = namespacename + '::' + classname
        name_func = classnamenet + '::' + name_func
        # seems to be that it will optimize this out from time to time, but the obj is
        # supposed to be there
        # if fieldstr[0] == 'C':
        arglist += fieldtype(classnamenet, True)
        arglist += fieldsparsing(fieldstr)
    # format the output funcname
    return outfuncformat(name_func, arglist)

def main(args):
    from unit_tests import unittest
    if args.u == True:
        for i in unittest:
            print(cppfilt_gc(i))
    if args.funcname_unfilt != None:
        print(cppfilt_gc(args.funcname_unfilt))

if __name__ == "__main__":
    argparser = argparse.ArgumentParser('cppfilt_gc')
    argparser.add_argument('-u', action='store_true', help='perform unittest')
    argparser.add_argument('-f', '--funcname_unfilt', help='unfiltered gc func name i cpp')
    args = argparser.parse_args()
    main(args)

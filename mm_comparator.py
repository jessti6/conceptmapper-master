import re
import os
# import tkinter as tk  # comment out if compiling for online
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from io import StringIO

from lxml import etree
from networkx import *
# from tkinter import *  # comment out if compiling for online
# from tkinter import filedialog  # comment out if compiling for online
from xmldiff import main, formatting

# radio_box = tk.Tk()  # comment out if compiling for online

moved_list = []
extras_list = []
missing_list = []

saved_list = []
return_list = []

parentlist = []
childlist = []

printlistforkey = []
printlistforstudent = []
difference_list = []
same_list = []


printlist_keycrosslink = []
printlist_studentcrosslink = []
same_list_cross =[]
difference_list_cross = []



def run_it():
    # comment out all but last line if compiling for online
    # v = IntVar()
    # Radiobutton(radio_box, variable=v, value=0,
    #             fg='grey', bg='white', bd=2, padx=20, pady=10, width=45, indicatoron=0,
    #             text='CHOOSE A PROCEDURE:').pack(anchor=W)
    # Radiobutton(radio_box, variable=v, value=1,
    #             fg='white', bg='grey', bd=2, padx=20, pady=10, width=45, indicatoron=0,
    #             command=find_diffs, text='Compare a given network against a master (key)').pack(anchor=W)
    # Radiobutton(radio_box, variable=v, value=2,
    #             fg='white', bg='grey', bd=2, padx=20, pady=10, width=45, indicatoron=0,
    #             command=analyze_xml, text='Analyze a given network').pack(anchor=W)
    # radio_box.mainloop()
    quit()


def find_diffs():
    # comment out all but last line if compiling for online
    # file1 = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=[("MM files", "*.mm")])
    # file2 = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=[("MM files", "*.mm")])
    # set_in_motion_find_diffs(file1, file2)
    # print_it(set_output_path(file1, file2))
    # print_it2(set_output_path1(file1, file2))
    # radio_box.quit()
    return


def return_diffs(file1, file1name, file2, file2name):
    global return_list
    # return_list = []
    clear_array()
    set_in_motion_find_diffs(file1, file1name, file2, file2name)
    print_it('for_download', file2name)
    print_it2('for_download')
    return return_list


def clear_array():
    global return_list, same_list, same_list_cross, difference_list, difference_list_cross, moved_list, extras_list, missing_list, saved_list, parentlist,childlist,printlistforstudent,printlistforkey,printlist_keycrosslink, printlist_studentcrosslink
    moved_list = []
    extras_list = []
    missing_list = []
    saved_list = []
    # return_list = []
    parentlist = []
    childlist = []
    printlistforkey = []
    printlistforstudent = []
    difference_list = []
    same_list = []
    printlist_keycrosslink = []
    printlist_studentcrosslink = []
    same_list_cross = []
    difference_list_cross = []


def clear2():
    global return_list, same_list, same_list_cross, difference_list, difference_list_cross, moved_list, extras_list, missing_list, saved_list, parentlist, childlist, printlistforstudent, printlistforkey, printlist_keycrosslink, printlist_studentcrosslink
    moved_list = []
    extras_list = []
    missing_list = []
    saved_list = []
    return_list = []
    parentlist = []
    childlist = []
    printlistforkey = []
    printlistforstudent = []
    difference_list = []
    same_list = []
    printlist_keycrosslink = []
    printlist_studentcrosslink = []
    same_list_cross = []
    difference_list_cross = []


def set_in_motion_find_diffs(file1, file1name, file2, file2name):
    diff = ''
    diff = main.diff_files(file1name, file2name, formatter=formatting.XMLFormatter())

    for i in diff.splitlines():
        if re.search(r'\bdiff:\w+', i) or i.startswith('</node'):
            if not cull_line(i, 'TRUE'):
                categorize_it(i)

    keyfile(file1name)
    studentfile(file2name)
    compare(printlistforkey,printlistforstudent)
    key_crosslink(file1name)
    student_crosslink(file2name)
    compare_cross_link(printlist_keycrosslink,printlist_studentcrosslink)

    return


def set_output_path(path1, path2):
    if path1.lower().find('key') >= 0:
        return path2.replace('.mm', '.node-diff-from-key.txt')
    elif path2.lower().find('key') >= 0:
        return path1.replace('.mm', '.node-diff-from-key.txt')
    else:
        return ''


def set_output_path1(path1, path2):
    if path1.lower().find('key') >= 0:
        return path2.replace('.mm', '.link-diff-from-key.txt')
    elif path2.lower().find('key') >= 0:
        return path1.replace('.mm', '.link-diff-from-key.txt')
    else:
        return ''


def analyze_xml():
    # comment out all but last line if compiling for online
    # path1 = filedialog.askopenfilename(initialdir="/", title="Select file",
    #                                    filetypes=[("MM files", "*.mm"), ("XML files", "*.xml")])
    # g = networkx.readwrite.graphml.read_graphml(graphify_it(scrub_it(path1)))
    # r = networkx.degree_assortativity_coefficient(g)
    # print("%3.1f" % r)
    # radio_box.quit()
    return


def cull_line(xml_line, am_finding_diffs):
    if am_finding_diffs == 'TRUE':
        rtn = 0
        if has_attr(xml_line, 'FOLDED'):
            return 1
        if has_attr(xml_line, 'STYLE'):
            return 1
        if has_attr(xml_line, 'COLOR') or has_attr(xml_line, 'AutomaticEdgeColor'):
            return 1
        if has_attr(xml_line, 'POSITION'):
            return 1
        if has_attr(xml_line, 'HGAP_QUANTITY'):
            return 1
        if has_attr(xml_line, 'VSHIFT_QUANTITY'):
            return 1
        if find_counterpart(xml_line):
            return 1
    else:
        rtn = 1
        if xml_line.startswith('<map ') or xml_line.startswith('</map>'):
            return 0
        if xml_line.startswith('<node') or xml_line.startswith('</node>'):
            return 0
        # if xml_line.startswith('<edge') or xml_line == '</edge>':
        #   return 0
    return rtn


def find_counterpart(xml_line):
    # look for a saved earlier line that indicates an insert to this delete, or vice versa
    txt = get_attr_val(xml_line, 'TEXT')
    txt_d = txt + '|delete'
    txt_i = txt + '|insert'
    if has_attr(xml_line, 'diff:delete'):
        if txt_i in saved_list:
            saved_list.remove(txt_i)
            go_back_and_clear(txt)
            return 1
        else:
            saved_list.append(txt_d)
    elif has_attr(xml_line, 'diff:insert'):
        if txt_d in saved_list:
            saved_list.remove(txt_d)
            go_back_and_clear(txt)
            return 1
        else:
            saved_list.append(txt_i)
    return 0


def categorize_it(xml_line):
    new_line = clean_it(xml_line, 'TRUE')
    if new_line.strip() != '':
        if has_attr(xml_line, 'diff:delete'):
            missing_list.append(new_line)
        elif has_attr(xml_line, 'diff:insert'):
            extras_list.append(new_line)
        else:
            moved_list.append(new_line)
    return


def clean_it(xml_line, am_finding_diffs):
    new_line = xml_line
    new_line = remove_attr(new_line, 'CREATED')
    new_line = remove_attr(new_line, 'MODIFIED')
    new_line = remove_attr(new_line, 'ID')
    if am_finding_diffs == 'FALSE':
        new_line = remove_attr(new_line, 'FOLDED')
        new_line = remove_attr(new_line, 'STYLE')
        new_line = remove_attr(new_line, 'COLOR')
        new_line = remove_attr(new_line, 'POSITION')
    new_line = replace_segment(new_line, '=\"\"', '')
    new_line = remove_segment(new_line, 'diff:add-attr=\"TEXT\"')
    new_line = replace_segment(new_line, 'diff:update-attr=', 'UPDATES=')
    new_line = replace_segment(new_line, 'UPDATES=\"TEXT:', 'UPDATES=\"')
    new_line = remove_segment(new_line, '<diff:insert>')
    new_line = remove_segment(new_line, '</diff:insert>')
    if am_finding_diffs == 'TRUE':
        new_line = remove_segment(new_line, '<node')
        new_line = remove_segment(new_line, '</node>')
        new_line = remove_segment(new_line, '/>')
        new_line = remove_segment(new_line, '>')
        new_line = replace_segment(new_line, '&gt;', '>')
        new_line = replace_segment(new_line, '&lt;', '<')
    else:
        new_line = replace_segment(new_line, '&gt;', '_gt_')
        new_line = replace_segment(new_line, '&lt;', '_lt_')
    new_line = remove_segment(new_line, 'diff:delete')
    new_line = remove_segment(new_line, 'diff:insert')
    new_line = remove_segment(new_line, 'diff:update-attr')
    new_line = remove_attr(new_line, 'version')
    if am_finding_diffs == 'TRUE':
        if all_the_same(new_line, 'TEXT', 'UPDATES'):
            return ''
    new_line = ' ' + ' '.join(new_line.split())  # add a space as an indent, remove double spaces
    return new_line


def scrub_it(path):
    # replace characters and lines such that the structure is well-formed
    # input file can be a file with .mm or .xml extension; process differently
    f = open(path, 'r')
    s = ''
    t = ''
    if path.endswith('.xml'):
        for l in f:
            if l.startswith('<?xml'):
                t = t + l
            else:
                s = l.replace('/', '|')
                s = s.replace('<|', '</')
                s = s.replace(' |>', '/>')
                s = s.replace(' ', '_')
                s = s.replace('!', '_')
                s = s.replace('@', '_')
                s = s.replace('#', '_')
                s = s.replace('$', '_')
                s = s.replace('%', '_pct')
                s = s.replace('&gt;', '_gt_')
                s = s.replace('&lt;', '_lt_')
                s = s.replace('&', '_')
                s = s.replace('*', '_')
                s = s.replace('(', '_')
                s = s.replace(')', '_')
                s = s.replace('+', 'plus')
                s = s.replace('=', '_')
                s = s.replace('[', '_')
                s = s.replace(']', '_')
                s = s.replace('{', '_')
                s = s.replace('}', '_')
                s = s.replace('|', '_')
                s = s.replace(':', '_')
                s = s.replace(';', '_')
                s = s.replace("'", '_')
                s = s.replace(',', '_')
                s = s.replace('?', '_')
                s = s.replace('<0', '<Zero')
                s = s.replace('<1', '<One')
                s = s.replace('<2', '<Two')
                s = s.replace('<3', '<Three')
                s = s.replace('<4', '<Four')
                s = s.replace('<5', '<Five')
                s = s.replace('<6', '<Six')
                s = s.replace('<7', '<Seven')
                s = s.replace('<8', '<Eight')
                s = s.replace('<9', '<Nine')
                t = t + s
    else:
        for l in f:
            if not cull_line(l, 'FALSE'):
                t = t + clean_it(l, 'FALSE') + '\n'
    f.close()
    # write out the new file
    p = path.replace('.xml', '_tmp.xml').replace('.mm', '_tmp.mm')
    f = open(p, 'w')
    f.write(t)
    f.close()
    return p


def graphify_it(path):
    # replace lines such that the structure is well-formed as a graph
    f = open(path, 'r')
    s = ''
    t = ''
    for l in f:
        s = l.strip()
        if s.startswith('<map'):
            s = s.replace('<map', '<graphml>\n<graph')
        if s.endswith('/map>'):
            s = s.replace('/map>', '/graph>\n</graphml>')
        t = t + s + '\n'
    f.close()
    # write out the new file
    p = path
    f = open(p, 'w')
    f.write(t)
    f.close()
    return p


def all_the_same(xml_line, attr1, attr2):
    # a difference of only capitalization is not interesting
    if get_attr_val(xml_line, attr1).lower() == \
            get_attr_val(xml_line, attr2).lower():
        return 1
    return 0


def has_attr(xml_line, attr):
    if xml_line.find(attr) < 0:
        return 0
    return 1


def get_attr(xml_line, attr):
    tmp = xml_line
    if tmp.find(attr + ':') < 0:  # there may or may not be a colon
        q1 = tmp.find(attr)
    else:
        q1 = tmp.find(attr + ':')
    if tmp.find(';', q1 + 1) < 0:  # delimited by semicolon or quote
        q2 = tmp.find('"', q1 + 1)
    else:
        if tmp.find('" ', q1 + 1) < tmp.find(';', q1+1):
            q2 = tmp.find('" ', q1 + 1)
        else:
            q2 = tmp.find(';', q1 + 1) + 1
    return tmp[q1: q2]


def get_attr_val(xml_line, attr):
    q1 = xml_line.find(attr + '=') + len(attr) + 1  # first quote
    q2 = xml_line.find('"', q1 + 1) + 1  # second quote
    return xml_line[q1: q2]


def remove_attr(xml_line, attr):
    # remove as its own attribute
    tmp = xml_line.replace(attr + '=' + get_attr_val(xml_line, attr), '')
    # remove as part of diff showing update to the attribute
    tmp = tmp.replace(get_attr(tmp, attr), '')
    tmp = tmp.replace('  ', ' ')
    return tmp


def remove_segment(xml_line, segment):
    return replace_segment(xml_line, segment, '')


def replace_segment(xml_line, segment, new_segment):
    return xml_line.replace(segment, new_segment)


def deduplicate_it(my_list):  # list expected to be sorted
    i = 0
    j = len(my_list)
    while i < j - 1:
        if my_list[i] == my_list[i + 1]:
            del my_list[i + 1]
            i = i - 1  # re-check in case multiple duplicates
            j = j - 1  # the list is now one item shorter
        i = i + 1
    return


def go_back_and_clear(attr):
    # remove a previously saved item, if appropriate
    for i in moved_list:
        if attr in i:
            moved_list.remove(i)
            return
    for i in extras_list:
        if attr in i:
            extras_list.remove(i)
            return
    for i in missing_list:
        if attr in i:
            missing_list.remove(i)
            return
    return


def keyfile(file1):
    f = open(file1, 'r')
    # print(os.path.abspath(file1))
    # f = etree.parse(StringIO(f))

    for i in f:
        if i.startswith('<node') and not i.endswith('/>') and not i.endswith('/>\n'):
            if len(parentlist) > 0:
                childlist.append(get_attr_val(i, 'TEXT'))
                printsentence = 'the parent node is ' + parentlist[-1] + ' and the child node is ' + childlist[-1]
                printlistforkey.append(printsentence)
            parentlist.append(get_attr_val(i, 'TEXT'))
        elif i.startswith('<node') and (i.endswith('/>') or i.endswith('/>\n')):
            childlist.append(get_attr_val(i, 'TEXT'))
            printsentence = 'the parent node is ' + parentlist[-1] + ' and the child node is ' + childlist[-1]
            printlistforkey.append(printsentence)
        elif i == '</node>' or i == '</node>\n':
            if len(parentlist) > 0:
                del parentlist[-1]
    f.close()
    return


def studentfile(file2):
    f = open(file2, 'r')
    for i in f:
        if i.startswith('<node') and not i.endswith('/>') and not i.endswith('/>\n'):
            if len(parentlist) > 0:
                childlist.append(get_attr_val(i, 'TEXT'))
                printsentence = 'the parent node is ' + parentlist[-1] + ' and the child node is ' + childlist[-1]
                printlistforstudent.append(printsentence)
            parentlist.append(get_attr_val(i, 'TEXT'))
        elif i.startswith('<node') and (i.endswith('/>') or i.endswith('/>\n')):
            childlist.append(get_attr_val(i, 'TEXT'))
            printsentence = 'the parent node is ' + parentlist[-1] + ' and the child node is ' + childlist[-1]
            printlistforstudent.append(printsentence)
        elif i == '</node>' or i == '</node>\n':
            if len(parentlist) > 0:
                del parentlist[-1]
    f.close()
    return


def compare(printlistforkey, printlistforstudent):
    key = sorted(printlistforkey)
    student = sorted(printlistforstudent)

    for i in key:
        for j in student:
            if i == j:
                same_list.append(i)
                break
    for z in (key + student):
        if z not in same_list:
            difference_list.append(z)
    return


def key_crosslink(file1):
    child_list = []
    id_list = []
    id_list_parent = []
    getnode = []
    d = defaultdict(int)

    f = open(file1, 'r')
    prev = next(f).strip()
    for i in map(str.strip,f):
        if i.startswith('<node'):
            getnode.append(i)
        if i.startswith('<node') and not i.endswith('/>') and not i.endswith('/>\n'):
            d[prev, i] += 1
            prev = i
            # j = i[i+1]
            # j = next(i) #go to next line
        if i.startswith('<arrowlink'):
            id_list.append(get_attr_val(i,'DESTINATION')) #find the destination ID
            child_list.append(get_attr_val(prev, 'TEXT'))
                    # test = k.__getattribute__('ID')
                    # getid.append(test)
    for x in id_list:
        for id in getnode:
                    # one = (get_attr_val(x,'DESTINATION'))
            two  = (get_attr_val(id, 'ID'))
            if x == two:
                id_list_parent.append(get_attr_val(id,'TEXT')) #
                printsentence = 'parent node: ' + id_list_parent[-1] + ' child node: ' + child_list[0]
                printlist_keycrosslink.append(printsentence)
                del child_list[0]
    # print(printlist_keycrosslink)
    f.close()
    return

def student_crosslink(file2):
    child_list = []
    id_list = []
    id_list_parent = []
    getnode = []
    d = defaultdict(int)

    f = open(file2, 'r')
    prev = next(f).strip()
    for i in map(str.strip, f):
        if i.startswith('<node'):
            getnode.append(i)
        if i.startswith('<node') and not i.endswith('/>') and not i.endswith('/>\n'):
            d[prev, i] += 1
            prev = i
        if i.startswith('<arrowlink'):
            id_list.append(get_attr_val(i, 'DESTINATION'))  # find the destination ID
            child_list.append(get_attr_val(prev, 'TEXT'))
    for x in id_list:
        for id in getnode:
            two = (get_attr_val(id, 'ID'))
            if x == two:
                id_list_parent.append(get_attr_val(id, 'TEXT'))  #
                printsentence = 'parent node: ' + id_list_parent[-1] + ' child node: ' + child_list[0]
                printlist_studentcrosslink.append(printsentence)
                del child_list[0]
    f.close()
    return

def compare_cross_link(printlist_keycrosslink, printlist_studentcrosslink):
    key = sorted(printlist_keycrosslink)
    student = sorted(printlist_studentcrosslink)

    for i in key:
        for j in student:
            if i == j:
                same_list_cross.append(i)
                break
    for z in (key + student):
        if z not in same_list_cross:
            difference_list_cross.append(z)
    return


def print_it(output_path, file2):
    global return_list
    moved_list.sort()
    deduplicate_it(moved_list)
    extras_list.sort()
    deduplicate_it(extras_list)
    missing_list.sort()
    deduplicate_it(missing_list)
    if output_path == '':
        print('Missing:' + '\n')
        print('\n'.join(missing_list))
        print('\n' + 'Extras:' + '\n')
        print('\n'.join(extras_list))
        print('\n' + 'Moved:' + '\n')
        print('\n'.join(moved_list))
    elif output_path == 'for_download':
        return_list.append('\n')
        return_list.append('student file name: ' + file2 +'\n')
        return_list.append('Missing Nodes: ' + '(Count:' + str(len(missing_list)) + ')')
        for i in missing_list:
            return_list.append(i)
        return_list.append('Extras Nodes: ' + '(Count:' + str(len(extras_list)) + ')')
        for i in extras_list:
            return_list.append(i)
        return_list.append('Moved Nodes: ' + '(Count:' + str(len(moved_list)) + ')')
        for i in moved_list:
            return_list.append(i)
    else:
        f = open(output_path, 'w')
        f.write('Missing:' + '\n')
        f.write('\n'.join(missing_list))
        f.write('\n' + 'Extras:' + '\n')
        f.write('\n'.join(extras_list))
        f.write('\n' + 'Moved:' + '\n')
        f.write('\n'.join(moved_list))
        f.close()
    return


def print_it2(output_path):
    global return_list
    if output_path == '':
        print('Same:' + '\n')
        print('\n'.join(same_list))
        print('\n' + 'Different:' + '\n')
        print('\n'.join(difference_list))
    elif output_path == 'for_download':
        # x = set(same_list)
        return_list.append('Same Link: ' + '(Count:' + str(len(same_list)) + ')')
        for i in same_list:
            return_list.append(i)
        # x = set(difference_list)
        return_list.append('Different Link: ' + '(Count:' + str(len(difference_list)) + ')')
        for i in difference_list:
            return_list.append(i)
        # x = set(same_list_cross)
        return_list.append('Same Cross Link: ' + '(Count:' + str(len(same_list_cross)) + ')')
        for i in same_list_cross:
            return_list.append(i)
        # x = set(difference_list_cross)
        return_list.append('Different Cross Link: ' + '(Count:' + str(len(difference_list_cross)) + ')')
        for i in difference_list_cross:
            return_list.append(i)

    else:
        f = open(output_path, 'w')
        f.write('Same:' + '\n')
        f.write('\n'.join(same_list))
        f.write('\n' + 'Different:' + '\n')
        f.write('\n'.join(difference_list))
        f.close()
    return


#run_it()  # comment out if compiling for online

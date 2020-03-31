import re
from collections import defaultdict
from xmldiff import main, formatting

# comment out next four lines if compiling for online
# import tkinter as tk
# from tkinter import *
# from tkinter import filedialog
# radio_box = tk.Tk()

moved_list = []
extras_list = []
missing_list = []

saved_list = []
return_list = []

child_list = []
parent_list = []

key_node = []

print_list_for_key = []
print_list_for_student = []

print_list_key_crosslink = []
print_list_student_crosslink = []

same_list = []
same_list_cross = []
difference_list = []
difference_list_cross = []
key_file_list = []
student_file_list = []


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
    # print_for_node('', set_output_path(file1, file2, 'node'))
    # print_for_link('')  # , set_output_path(file1, file2, 'link'))
    # radio_box.quit()
    return


def return_diffs(file1, file2):
    global return_list
    clear_arrays()
    set_in_motion_find_diffs(file1, file2)
    print_for_node('for_download', file2)
    print_for_link('for_download')
    return return_list


def clear_arrays():
    global same_list, same_list_cross, difference_list, difference_list_cross, moved_list, \
        extras_list, missing_list, saved_list, parent_list, child_list, print_list_for_student, \
        print_list_for_key, print_list_key_crosslink, print_list_student_crosslink, key_node

    moved_list = []
    extras_list = []
    missing_list = []
    saved_list = []
    parent_list = []
    child_list = []
    print_list_for_key = []
    print_list_for_student = []
    key_node = []
    difference_list = []
    same_list = []
    print_list_key_crosslink = []
    print_list_student_crosslink = []
    same_list_cross = []
    difference_list_cross = []
    key_file_list = []


def clear_all_vars():
    global return_list
    return_list = []
    clear_arrays()


def set_in_motion_find_diffs(file1name, file2name):
    diff = ''
    diff = main.diff_files(file1name, file2name, formatter=formatting.XMLFormatter())


    for i in diff.splitlines():
        # if i.find('Etiology') > 0:
        #     x =1
        if re.search(r'\bdiff:\w+', i) or i.startswith('</node'):
            if not cull_line(i, 'TRUE'):
                categorize_it(i)
    get_all_node_from_keyfile(file1name) #double check the missing and extra list
    get_all_node_from_studentfile(file2name)
    key_file(file1name)
    student_file(file2name)
    compare(print_list_for_key, print_list_for_student)
    key_crosslink(file1name)
    student_crosslink(file2name)
    compare_crosslink(print_list_key_crosslink, print_list_student_crosslink)

    return


def set_output_path(path1, path2, node_or_link):
    if path1.lower().find('key') >= 0:
        return path2.replace('.mm', '.' + node_or_link + '-diff-from-key.txt')
    elif path2.lower().find('key') >= 0:
        return path1.replace('.mm', '.' + node_or_link + '-diff-from-key.txt')
    else:
        # presume first arg points to key
        return path2.replace('.mm', '.' + node_or_link + '-diff-from-key.txt')


def analyze_xml():  # networkx=None):
    # comment out all but last line if compiling for online
    # path1 = filedialog.askopenfilename(initialdir="/", title="Select file",
    #                                    filetypes=[("MM files", "*.mm"), ("XML files", "*.xml")])
    # g = networkx.readwrite.graphml.read_graphml(graphify_it(scrub_it(path1)))
    # r = networkx.degree_assortativity_coefficient(g)
    # print("%3.1f" % r)
    # radio_box.quit()
    return


def cull_line(xml_line, am_finding_diffs):
    if is_the_same(am_finding_diffs, 'TRUE'):
        rtn = 0
        if has_attr(xml_line, 'FOLDED'):
            return 1
        if has_attr(xml_line, 'STYLE'):
            return 1
        if has_attr(xml_line, 'COLOR') or has_attr(xml_line, 'AutomaticEdgeColor'):
            return 1
        # try delete position
        # if has_attr(xml_line, 'POSITION'):
        #     return 1
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
        # if xml_line.startswith('<edge') or is_the_same(xml_line, '</edge>'):
        #     return 0
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
    if not is_the_same(new_line, ''):
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
    new_line = remove_attr(new_line, 'POSITION')
    if is_the_same(am_finding_diffs, 'FALSE'):
        new_line = remove_attr(new_line, 'FOLDED')
        new_line = remove_attr(new_line, 'STYLE')
        new_line = remove_attr(new_line, 'COLOR')
        new_line = remove_attr(new_line, 'POSITION')
    new_line = replace_segment(new_line, '=\"\"', '')
    # new_line = remove_segment(new_line, 'diff:add-attr=\"TEXT\"')
    new_line = replace_segment(new_line, 'diff:add-attr=\"TEXT\"', 'UPDATES=')
    new_line = replace_segment(new_line, 'diff:update-attr=', 'UPDATES=')
    new_line = replace_segment(new_line, 'UPDATES=\"TEXT:', 'UPDATES=\"')
    new_line = remove_segment(new_line, '<diff:insert>')
    new_line = remove_segment(new_line, '</diff:insert>')
    if is_the_same(am_finding_diffs, 'TRUE'):
        new_line = remove_segment(new_line, '<node')
        new_line = remove_segment(new_line, '</node>')
        new_line = remove_segment(new_line, '/>')
        new_line = remove_segment(new_line, '>')
        new_line = un_html_it(new_line)
    else:
        new_line = replace_segment(new_line, '&gt;', '_gt_')
        new_line = replace_segment(new_line, '&lt;', '_lt_')
    new_line = remove_segment(new_line, 'diff:delete')
    new_line = remove_segment(new_line, 'diff:insert')
    new_line = remove_segment(new_line, 'diff:update-attr')
    new_line = remove_attr(new_line, 'version')
    if is_the_same(am_finding_diffs, 'TRUE'):
        if all_the_same(new_line, 'TEXT', 'UPDATES'):
            return ''
    if new_line.find('richcontent') != -1:
        if is_the_same(get_attr(new_line, 'TEXT'), ''):
            new_line = ''
    elif new_line.endswith('UPDATES=\"'):
        new_line = replace_segment(new_line, 'UPDATES=\"', '')
    new_line = replace_segment(new_line, 'UPDATES=', '')
    new_line = ' ' + ' '.join(new_line.split())  # add a space as an indent, remove double spaces
    return new_line


def un_html_it(line):
    # replace HTML-like substrings
    s = line
    s = s.replace('&gt;', '>')
    s = s.replace('&lt;', '<')
    return s


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

        # top and bottom of graph structure
        if s.startswith('<map'):
            s = s.replace('<map', '<graphml>\n<graph')
        if s.endswith('/map>'):
            s = s.replace('/map>', '/graph>\n</graphml>')

        # otherwise it's a node...
        if s.startswith('<node'):

            a = get_attr_val(s, 'TEXT')

            # no matter what, print out as a self-contained node element
            _s = s.replace('TEXT', 'ID').replace('>', '/>').replace('//', '/')

            # if a child node, print out edge to parent
            if len(parent_list) > 0:
                _s = _s + '\n' + '<edge source=' + parent_list[-1] + ' target=' + a + '/>'

            # if a parent node, prep for its children
            if not s.endswith('/>') and not s.endswith('/>\n'):
                parent_list.append(a)

            s = _s
        else:
            # ...or an end tag
            if is_the_same(s, '</node>') or is_the_same(s, '</node>\n'):
                s = ''
                if len(parent_list) > 0:
                    del parent_list[-1]

        t = t + s + '\n'
    f.close()

    # write out the new file
    p = path
    f = open(p, 'w')
    f.write(t)
    f.close()
    return p


def all_the_same(xml_line, attr1, attr2):
    if is_the_same(get_attr_val(xml_line, attr1), get_attr_val(xml_line, attr2)):
        return 1
    return 0


def is_the_same(val1, val2):
    # a difference of only capitalization is not interesting
    if val1.strip().lower() == val2.strip().lower():
        return 1
    return 0


def has_attr(xml_line, attr):
    if xml_line.find(attr) < 0:
        return 0
    # if xml_line.find('/' + attr) < xml_line.find(attr) and xml_line.find('/' + attr) >= 0:
    #     return 0
    return 1


def get_attr(xml_line, attr):
    tmp = xml_line
    if tmp.find(attr + ':') < 0:  # there may or may not be a colon
        q1 = tmp.find(attr)
    else:
        q1 = tmp.find(attr + ':')
    if tmp.find(';', q1 + 1) < 0:  # delimited by semicolon or quote
        q2 = tmp.find('"', q1 + 1)
    # else:
    #     x = tmp.find('" ', q1 + 1)
    #     y = tmp.find(';', q1 + 1)
    #     if tmp.find('" ', q1 + 1) < tmp.find(';', q1 + 1) and x >= 0:
    #         q2 = tmp.find('" ', q1 + 1)
    #     else:
    #         q2 = tmp.find(';', q1 + 1) + 1
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
        if is_the_same(my_list[i], my_list[i + 1]):
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

def get_all_node_from_keyfile(keyfile):
    f = open(keyfile, 'r')
    for i in f:
        if i.startswith('<node'):
            key_file_list.append(get_attr_val(i, 'TEXT').lower())
    return

def get_all_node_from_studentfile(studentfile):
    f = open(studentfile, 'r')
    for i in f:
        if i.startswith('<node'):
            student_file_list.append(get_attr_val(i, 'TEXT').lower())
    double_check()
    return


def double_check():
    for i in missing_list:
        x = get_attr_val(i, 'TEXT').lower()
        if x not in key_file_list:
            missing_list.remove(i)
            double_check()
    for i in extras_list:
        x = get_attr_val(i, 'TEXT').lower()
        if x in key_file_list:
            extras_list.remove(i)
            double_check()
    for i in moved_list:
        x = get_attr_val(i, 'TEXT').lower()
        if x not in key_file_list:
            moved_list.remove(i)
            extras_list.append(i)
            double_check()
        elif x in key_file_list and x not in student_file_list:
            moved_list.remove(i)
            missing_list.append(i)
            double_check()

    return


def key_file(file1):
    _p = 'The parent node is '
    _c = ' and the child node is '
    f = open(file1, 'r')
    for i in f:
        if i.startswith('<node') and not i.endswith('/>') and not i.endswith('/>\n'):
            if len(key_node) == 0:
                key_node.append(get_attr_val(i, 'TEXT'))
            if len(parent_list) > 0:
                child_list.append(get_attr_val(i, 'TEXT'))
                print_sentence = _p + un_html_it(parent_list[-1]) + _c + un_html_it(child_list[-1])
                print_list_for_key.append(print_sentence)
            parent_list.append(get_attr_val(i, 'TEXT'))
        elif i.startswith('<node') and (i.endswith('/>') or i.endswith('/>\n')):
            child_list.append(get_attr_val(i, 'TEXT'))
            print_sentence = _p + un_html_it(parent_list[-1]) + _c + un_html_it(child_list[-1])
            print_list_for_key.append(print_sentence)
        elif is_the_same(i, '</node>') or is_the_same(i, '</node>\n'):
            if len(parent_list) > 0:
                del parent_list[-1]
    f.close()
    return


def student_file(file2):
    _p = 'The parent node is '
    _c = ' and the child node is '
    f = open(file2, 'r')
    for i in f:
        if i.startswith('<node') and not i.endswith('/>') and not i.endswith('/>\n'):
            if len(parent_list) > 0:
                child_list.append(get_attr_val(i, 'TEXT'))
                print_sentence = _p + un_html_it(parent_list[-1]) + _c + un_html_it(child_list[-1])
                print_list_for_student.append(print_sentence)
            parent_list.append(get_attr_val(i, 'TEXT'))
            if not is_the_same(parent_list[0], key_node[0]):
                parent_list[0] = key_node[0]  # ignore if root node values are unequal
        elif i.startswith('<node') and (i.endswith('/>') or i.endswith('/>\n')):
            child_list.append(get_attr_val(i, 'TEXT'))
            print_sentence = _p + un_html_it(parent_list[-1]) + _c + un_html_it(child_list[-1])
            print_list_for_student.append(print_sentence)
        elif is_the_same(i, '</node>') or is_the_same(i, '</node>\n'):
            if len(parent_list) > 0:
                del parent_list[-1]
    f.close()
    return


def compare(print_listforkey, print_listforstudent):
    key = sorted(print_listforkey)
    student = sorted(print_listforstudent)

    for i in key:
        for j in student:
            if is_the_same(i, j):
                same_list.append(i)
                break
    for z in (key + student):
        if z not in same_list:
            difference_list.append(z)
    return


def key_crosslink(file1):
    _p = 'The parent node is '
    _c = ' and the child node is '
    child_list = []
    id_list = []
    id_list_parent = []
    getnode = []
    d = defaultdict(int)

    f = open(file1, 'r')
    prev = next(f).strip()
    for i in map(str.strip, f):
        if i.startswith('<node'):
            getnode.append(i)
        if i.startswith('<node') and not i.endswith('/>') and not i.endswith('/>\n'):
            d[prev, i] += 1
            prev = i
            # j = i[i+1]
            # j = next(i) #go to next line
        if i.startswith('<arrowlink'):
            id_list.append(get_attr_val(i, 'DESTINATION'))  # find the destination ID
            child_list.append(get_attr_val(prev, 'TEXT'))
    for x in id_list:
        for id in getnode:
            # one = (get_attr_val(x,'DESTINATION'))
            two = (get_attr_val(id, 'ID'))
            if is_the_same(x, two):
                id_list_parent.append(get_attr_val(id, 'TEXT'))  #
                print_sentence = _p + un_html_it(id_list_parent[-1]) + _c + un_html_it(child_list[0])
                print_list_key_crosslink.append(print_sentence)
                del child_list[0]
    f.close()
    return


def student_crosslink(file2):
    _p = 'The parent node is '
    _c = ' and the child node is '
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
            if is_the_same(x, two):
                id_list_parent.append(get_attr_val(id, 'TEXT'))  #
                print_sentence = _p + un_html_it(id_list_parent[-1]) + _c + un_html_it(child_list[0])
                print_list_student_crosslink.append(print_sentence)
                del child_list[0]
    f.close()
    return


def compare_crosslink(prt_key_crosslink, prt_student_crosslink):
    key = sorted(prt_key_crosslink)
    student = sorted(prt_student_crosslink)

    for i in key:
        for j in student:
            if is_the_same(i, j):
                same_list_cross.append(i)
                break
    for z in (key + student):
        if z not in same_list_cross:
            difference_list_cross.append(z)
    return


def print_for_node(output_path, file2):
    global return_list
    moved_list.sort()
    deduplicate_it(moved_list)
    extras_list.sort()
    deduplicate_it(extras_list)
    missing_list.sort()
    deduplicate_it(missing_list)
    _s = 'Student file name: ' + file2 + '\n'
    _k = 'Top node: ' + key_node[0] + '\n'
    _m = 'Missing nodes: ' + '(Count: ' + str(len(missing_list)) + ')' + '\n'
    _e = 'Extra nodes: ' + '(Count: ' + str(len(extras_list)) + ')' + '\n'
    _v = 'Moved nodes: ' + '(Count: ' + str(len(moved_list)) + ')' + '\n'
    if is_the_same(output_path, ''):
        print(_s)
        print(_k)
        print(_m)
        print('\n'.join(missing_list))
        print('\n' + _e)
        print('\n'.join(extras_list))
        print('\n' + _v)
        print('\n'.join(moved_list))
    elif is_the_same(output_path, 'for_download'):
        # return_list.append('\n')
        return_list.append(_s)
        return_list.append(_k)
        return_list.append(_m)
        for i in missing_list:
            return_list.append(i)
        return_list.append('\n' + _e)
        for i in extras_list:
            return_list.append(i)
        return_list.append('\n' + _v)
        for i in moved_list:
            return_list.append(i)
    else:
        f = open(output_path, 'w')
        f.write(_s)
        f.write(_k)
        f.write(_m)
        f.write('\n'.join(missing_list))
        f.write('\n' + _e)
        f.write('\n'.join(extras_list))
        f.write('\n' + _v)
        f.write('\n'.join(moved_list))
        f.close()
    return


def print_for_link(output_path):
    global return_list
    _sl = 'Same link: ' + '(Count: ' + str(len(same_list)) + ')' + '\n'
    _dl = 'Different link: ' + '(Count: ' + str(len(difference_list)) + ')' + '\n'
    _sx = 'Same cross link: ' + '(Count: ' + str(len(same_list_cross)) + ')' + '\n'
    _dx = 'Different cross link: ' + '(Count: ' + str(len(difference_list_cross)) + ')' + '\n'
    if is_the_same(output_path, ''):
        print('\n' + _sl)
        print('\n'.join(same_list))
        print('\n' + _dl)
        print('\n'.join(difference_list))
        print('\n' + _sx)
        print('\n'.join(same_list_cross))
        print('\n' + _dx)
        print('\n'.join(difference_list_cross))
    elif is_the_same(output_path, 'for_download'):
        return_list.append('\n' + _sl)
        for i in same_list:
            return_list.append(i)
        return_list.append('\n' + _dl)
        for i in difference_list:
            return_list.append(i)
        return_list.append('\n' + _sx)
        for i in same_list_cross:
            return_list.append(i)
        return_list.append('\n' + _dx)
        for i in difference_list_cross:
            return_list.append(i)
    else:
        f = open(output_path, 'w')
        f.write('\n' + _sl)
        f.write('\n'.join(same_list))
        f.write('\n' + _dl)
        f.write('\n'.join(difference_list))
        f.write('\n' + _sx)
        f.write('\n'.join(same_list_cross))
        f.write('\n' + _dx)
        f.write('\n'.join(difference_list_cross))
        f.close()
    return

# run_it()  # comment out if compiling for online


import os

from flask import flash, request, redirect, render_template

import mm_comparator
from app import app
from lib.flask import Response

Extensions = 'mm'
Allowed_extensions = set([Extensions])

diffs = ''
file_name = ''
# out_directory = os.path.expanduser('~').replace('\\', '\\\\')

key_file_sav = {''}
key_file_name_sav = ''

student_file_name_sav = ''
student_filenames = ''

q_repeated = False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Allowed_extensions


def check_inputs(file1, file2):
    if file1.filename == '' and key_file_name_sav == '':
        return 'No key file selected for uploading'
    elif file2.filename == '':
        return 'No student data file selected for uploading'
    elif not allowed_file(file1.filename) and key_file_name_sav == '':
        return 'Allowed key files have ' + Extensions + ' extension'
    elif not allowed_file(file2.filename):
        return 'Allowed student data files have ' + Extensions + ' extension'
    return ''


@app.route('/')
def upload_form():
    context = {'repeated': q_repeated, 'key_file': key_file_name_sav, 'student_file': student_file_name_sav,
               'filenames': student_filenames}
    return render_template('upload.html', context=context)


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        global key_file_sav, key_file_name_sav, student_file_name_sav
        key_file = request.files['key_file']
        key_file.save(os.path.join(app.config['UPLOAD_FOLDER'], key_file.filename))
        student_file = request.files.getlist("student_file[]")
        for i in student_file:
            i.save(os.path.join(app.config['UPLOAD_FOLDER'], i.filename))

        for i in student_file:
            if check_inputs(key_file, i) != '':
                flash(check_inputs(key_file, i))
                return redirect(request.url)

        # good to go, run the comparison
        global diffs, file_name

        for i in student_file:
            # diffs = mm_comparator.return_diffs(key_file, key_file.filename, i, i.filename)
            diffs = mm_comparator.return_diffs(key_file.filename, i.filename)
            file_name = mm_comparator.set_output_path(key_file.filename, i.filename, 'node_and_links')

        return redirect('/out')


@app.route("/out")
def get():
    # global q_repeated
    # q_repeated = True
    mm_comparator.clear_all_vars()
    return render_template('download.html')


@app.route("/get_download")
def get_download():
    global diffs, file_name

    with open(file_name, 'w') as f:
        empty = os.stat(file_name).st_size == 0
        if empty:
            print(diffs)
            for i in diffs:
                f.write(i)
                f.write('\n')
            del diffs
            f.close()
        else:
            f.close()
            file_name.seek(0)
            file_name.truncate()
            with open(file_name, 'w') as g:
                for i in diffs:
                    g.write(i)
                    g.write('\n')
            g.close()

    with open(file_name, 'r') as h:
        diff = h.read()
        h.close()
        return Response(
            diff,
            mimetype="text",
            headers={"Content-disposition": "attachment; filename=diff.txt"})


if __name__ == "__main__":
    # app.debug = True
    app.run(host='0.0.0.0', port=8080)
    # app.run()

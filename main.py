import os

from flask import flash, request, redirect, render_template, make_response

import mm_comparator
from app import app
from lib.flask import Response

Extensions = 'mm'
Allowed_extensions = set([Extensions])

diffs = ''
file_name = ''
out_directory = os.path.expanduser('~').replace('\\', '\\\\')

key_file_sav = {''}
key_file_name_sav = ''

student_file_name_sav = ''

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
    context = {'repeated': q_repeated, 'key_file': key_file_name_sav, 'student_file': student_file_name_sav}
    return render_template('upload.html', context=context)


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        global key_file_sav, key_file_name_sav, student_file_name_sav
        key_file = request.files['key_file']
        student_file = request.files['student_file']
        if check_inputs(key_file, student_file) != '':
            flash(check_inputs(key_file, student_file))
            return redirect(request.url)
        # good to go, run the comparison
        global diffs, file_name
        if key_file.filename != key_file_name_sav and key_file.filename != '':
            key_file_sav = key_file
            key_file_name_sav = key_file.filename
        if student_file.filename != student_file_name_sav and student_file.filename != '':
            student_file_name_sav = student_file.filename
        diffs = mm_comparator.return_diffs(key_file_sav, key_file_name_sav, student_file, student_file_name_sav)
        # print(os.path.abspath(key_file_name_sav))
		# /Users/Tingting/conceptmapper/data/Osteoporosis_key.mm
        # diffs = mm_comparator.return_diffs(os.path.abspath(key_file_sav), student_file)

        file_name = mm_comparator.set_output_path(key_file_name_sav, student_file.filename)
        return redirect('/out')


# @app.route("/out")
# def getFile():
#     headers = {"Content-Disposition": "attachment; filename=%s" % file_name}
#     with open(file_name, 'w') as f:
#         for i in diffs:
#             f.write(i)
#             f.write('\n')
#         f.close()
#         body = f
#         # resp = make_response(headers,body)
#         global q_repeated
#         q_repeated = True
#
#         return render_template('download.html' )

    # return make_response((body, headers))

# def download_file():
#     headers = {"Content-Disposition": "attachment; filename=%s" % file_name}
#     with open(file_name, 'w') as f:
#         for i in diffs:
#             f.write(i)
#             f.write('\n')
#         f.close()
#         body = f
#         return make_response(headers,body)
#download 成功
#接下来实现按go 进入download页面
#按download 返回



@app.route("/out")
def get():
    with open(file_name, 'w') as f:
        for i in diffs:
            f.write(i)
            f.write('\n')
        f.close()
    global q_repeated
    q_repeated = True
    return render_template('download.html' )

@app.route("/getDownload")
def getDownload():

    with open(file_name) as f:
        diff = f.read()
        # for i in diffs:
        #     f.write(i)
        #     f.write('\n')
        # f.close()
        # return render_template('complete.html')
    return Response(
        diff,
        mimetype="text",
        headers={"Content-disposition":
                     "attachment; filename=diff.txt"})




#download view
# @app.route('/out')
# def download_form():
#     global out_directory
#     context = {'out_directory': out_directory}
#     return render_template('download.html', context=context)

#  download view
# @app.route('/out/<path:filename>', methods=['GET', 'POST'])
# def download(filename):
#     save_it_out()
#     outPath = os.path.join(current_app.root_path, file_name)
#     return send_from_directory(directory=outPath, filename=filename)


# def download1():
#     file = open(os.path.join(current_app.root_path, file_name), 'w')
#     for i in diffs:
#         file.write(i)
#         file.write('\n')
#     file.close()
#     return download(file)

# @app.route('/<filename>')
# def download(filname):
#     return



# @app.route('/out', methods=['POST'])
# def download_file():
#     if request.method == 'POST':
#         global out_directory
#         out_directory = request.form['out_path']
#         if out_directory == '':
#             flash('No directory selected for downloading')
#             return redirect(request.url)
#         # good to go, run the comparison
#         getdifferent_file()
#         # save_it_out()
#         flash('Comparison file successfully downloaded')
#         global q_repeated
#         q_repeated = True
#         return redirect('/')
#
#
# @app.route("/out")
# def getdifferent_file():
#     # global out_directory
#     # out_directory = request.form['out_path']
#     file = open(os.path.join(current_app.root_path, file_name), 'w')
#     for i in diffs:
#         file.write(i)
#         file.write('\n')
#     file.close()
#     return Response(
#         mimetype="text",
#         headers={"Content-disposition":
#                  "attachment;"})
#


# def save_it_out():
#     global out_directory, file_name, diffs
#     # if out_directory[len(out_directory)-1] != '\\':
#     # 	out_directory += '\\'
#     file = open(os.path.join(current_app.root_path, file_name), 'w')
#     for i in diffs:
#         file.write(i)
#         file.write('\n')
#     file.close()
#     return
#     Response(
#         mimetype="text",
#         headers={"Content-disposition":
#                  "attachment; filename=different.txt"})






if __name__ == "__main__":
    app.debug = True
    # app.run(host='0.0.0.0', port=8080)
    app.run()
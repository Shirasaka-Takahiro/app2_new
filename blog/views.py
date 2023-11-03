from flask import render_template, request, redirect, url_for, flash
from blog import app
from random import randint
from blog import db
from blog.models.employee import Employee
from blog.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from blog import login_manager
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
import subprocess
import os
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    my_dict = {
        'insert_something1': 'views.pyのinsert_something1部分です。',
        'insert_something2': 'views.pyのinsert_something2部分です。',
        'test_titles': ['title1', 'title2', 'title3']
    }
    return render_template('testapp/index.html', my_dict=my_dict)

@app.route('/test')
def other1():
    return render_template('testapp/index2.html')

##じゃんけん機能
@app.route('/sampleform', methods=['GET', 'POST'])
@login_required
def sample_form():
    if request.method == 'GET':
        return render_template('testapp/sampleform.html')
    elif request.method == 'POST':
        hands = {
            '0': 'グー',
            '1': 'チョキ',
            '2': 'パー',
        }
        janken_mapping = {
            'draw': '引き分け',
            'win': '勝ち',
            'lose': '負け',
        }

        player_hand_ja = hands[request.form['janken']]
        player_hand = int(request.form['janken'])
        enemy_hand = randint(0,2)
        enemy_hand_ja = hands[str(enemy_hand)]
        if player_hand == enemy_hand:
            judgement = 'draw'
        elif (player_hand == 0 and enemy_hand == 1) or (player_hand == 1 and enemy_hand == 2) or (player_hand == 2 and enemy_hand == 0):
            judgement = 'win'
        else:
            judgement = 'lose'
        result = {
            'enemy_hand_ja': enemy_hand_ja,
            'player_hand_ja': player_hand_ja,
            'judgement': janken_mapping[judgement],
        }
        return render_template('testapp/janken_result.html', result=result)

##従業員追加機能
@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'GET':
        return render_template('testapp/add_employee.html')
    elif request.method == 'POST':
        form_name = request.form.get('name')
        form_mail = request.form.get('mail')
        form_is_remote = request.form.get('is_remote', default=False, type=bool)
        form_department = request.form.get('department')
        form_year = request.form.get('year', default=0, type=int)

        employee = Employee(
            name = form_name,
            mail = form_mail,
            is_remote = form_is_remote,
            department = form_department,
            year = form_year 
        )
        db.session.add(employee)
        db.session.commit()
        flash('従業員を追加しました。', 'success')
        return redirect(url_for('index'))

@app.route('/employees')
@login_required
def employee_list():
    employees = Employee.query.all()
    return render_template('testapp/employee_list.html', employees=employees)

@app.route('/employees/<int:id>')
@login_required
def employee_detail(id):
    employee = Employee.query.get_or_404(id)
    return render_template('testapp/employee_detail.html', employee=employee)

@app.route('/employees/<int:id>/edit', methods=['GET'])
@login_required
def employee_edit(id):
    employee = Employee.query.get(id)
    return render_template('testapp/employee_edit.html', employee=employee)

@app.route('/employees/<int:id>/update', methods=['POST'])
@login_required
def employee_update(id):
    employee = Employee.query.get(id)
    employee.name = request.form.get('name')
    employee.mail = request.form.get('mail')
    employee.is_remote = request.form.get('is_remote', default=False, type=bool)
    employee.department = request.form.get('department')
    employee.year = request.form.get('year', default=0, type=int)

    db.session.merge(employee)
    db.session.commit()
    flash('編集が完了しました。', 'success')
    return redirect(url_for('employee_list'))

@app.route('/employees/<int:id>/delete', methods=['POST'])
@login_required
def employee_delete(id):
    employee = Employee.query.get(id)
    db.session.delete(employee)
    db.session.commit()
    flash('削除が完了しました。', 'success')
    return redirect(url_for('employee_list'))


##ユーザー認証機能
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User(
            username=username, 
            password=generate_password_hash(password, method='sha256')
        )
        db.session.add(user)
        db.session.commit()
        flash('ユーザー登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('index'))
    else:
        return render_template('testapp/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            flash('ログインに成功しました。', 'success')
            return redirect(url_for('index'))
        else:
            flash('ログインに失敗しました。ユーザー名またはパスワードが正しくありません。', 'error')
            return redirect(url_for('index'))
    else:
        return render_template('testapp/login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('ログアウトに成功しました。', 'success')
    return redirect(url_for('index'))

@app.route('/user_detail/<int:id>', methods=['GET'])
def user_detail(id):
    user = User.query.get(id)
    return render_template('testapp/user_detail.html', user=user)

@app.route('/tf_init', methods=['POST', 'GET'])
@login_required
def tf_init():
    if request.method == 'POST':
        try:
            # terraform initを実行
            init_result = subprocess.run(['terraform', 'init'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            return f'Terraform init output: {init_result.stdout}'
        except subprocess.CalledProcessError as e:
            return f'Error running Terraform init: {e.stderr}'
    return render_template('testapp/tf_exec.html')


UPLOAD_DIR = '/home/vagrant/.ssh/example.pub'

##Terraform実行機能
@app.route('/tf_plan', methods=['POST', 'GET'])
@login_required
def tf_plan():
    if request.method == 'POST':
        ##AWS環境変数設定
        #aws_access_key = request.form.get('aws_access_key')
        #aws_secret_key = request.form.get('aws_secret_key')
        #aws_region = request.form.get('aws_region')

        # 入力された値を環境変数としてセット
        #os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
        #os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_key
        #os.environ['AWS_DEFAULT_REGION'] = aws_region
        #flash('環境変数を設定しました', 'success')

        UPLOAD_DIR = '/home/vagrant/.ssh/'
        #public_key_file = request.files['public_key']
        public_key = request.form.get('public_key')
        #if public_key_file:
        if public_key:
            # セキュアなファイル名を生成して保存
            new_filename = 'example.pub'
            save_path = os.path.join(UPLOAD_DIR, new_filename)
            #public_key_file.save(save_path)
            with open(save_path, 'w') as f:
                f.write(public_key)
        
        # 必要なフィールドのいずれかが設定されていない場合、エラーメッセージをフラッシュ
        #if not aws_access_key or not aws_secret_key or not aws_region or not public_key:
        #    flash("AWS Access Key、AWS Secret Key、AWS Region、または公開鍵ファイルが入力されていません。", "error")
        #    return redirect(url_for('tf_exec'))

        ##terraform.tfvarsの作成
        project = request.form.get('project')
        env = request.form.get('env')
        access_key = request.form.get('aws_access_key')
        secret_key = request.form.get('aws_secret_key')

        tf_vars = {
            "general_config": {
                "project": project,
                "env": env
            },
            "access_key": access_key,
            "secret_key": secret_key
        }

        with open('/home/vagrant/app2_new/terrafomr_dir/alb_ec2_terraform/env/dev/terraform.tfvars.json', 'w') as f:
            json.dump(tf_vars, f)
        
        #subprocess.run(['terraform', 'init'], cwd='/home/vagrant/app2/terrafomr_dir/alb_ec2_terraform/env/dev')
        # コマンドを実行し、標準出力をバイト文字列として取得
        result = subprocess.Popen(['terraform', 'plan'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = result.communicate()

        # stdoutにはバイト文字列が含まれるので、デコードして文字列に変換
        stdout_str = stdout.decode('utf-8')
        stderr_str = stderr.decode('utf-8')

        # stdout_strには標準出力の文字列が、stderr_strには標準エラー出力の文字列が含まれる
        print(stdout_str)
        print(stderr_str)
    return render_template('testapp/tf_exec.html')

#@app.route('/tf_apply', methods=['POST'])
#@login_required
#def tf_apply():
#    if request.method == 'POST':
        # Terraform apply実行
#        result = subprocess.run(['terraform', 'apply', '-auto-approve'], cwd='/home/vagrant/_new/terrafomr_dir/alb_ec2_terraform/env/dev', capture_output=True, text=True)
#        return result.stdout
 #   return render_template('testapp/tf_exec.html')

#@app.route('/tf_destroy', methods=['POST'])
#@login_required
#def tf_destroy():
#    if request.method == 'POST':
        # terraform destroy実行
#        result = subprocess.run(['terraform', 'destroy', '-auto-approve'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_terraform/env/dev', capture_output=True, text=True)
#        return result.stdout
#    return render_template('testapp/tf_exec.html')

@app.route('/tf_exec_output')
@login_required
def execute_with_output(command, cwd, output_file):
    with open(output_file, 'w') as f:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, text=True)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            f.write(line)
            f.flush()
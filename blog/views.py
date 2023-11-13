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
import re

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


#AWSProfileの作成
@app.route('/create_aws_profile', methods=['GET', 'POST'])
def create_aws_profile():
    if request.method == 'POST':
        # フォームから入力された情報を取得
        profile_name = request.form['profile_name']
        aws_access_key = request.form['aws_access_key']
        aws_secret_key = request.form['aws_secret_key']
        region = request.form['region']
        output_format = request.form['output_format']

        # デフォルトリージョンと出力形式を設定
        try:
            subprocess.run([
                'aws', 'configure', 'set', 'region', region, '--profile', profile_name
            ])
            subprocess.run([
                'aws', 'configure', 'set', 'output', output_format, '--profile', profile_name
            ])
        except Exception as e:
            flash(f'デフォルトリージョンと出力形式の設定中にエラーが発生しました: {str(e)}', 'error')

        # AWSプロファイルの作成
        try:
            subprocess.run([
                'aws', 'configure', 'set', 'aws_access_key_id', aws_access_key, '--profile', profile_name
            ])
            subprocess.run([
                'aws', 'configure', 'set', 'aws_secret_access_key', aws_secret_key, '--profile', profile_name
            ])
            flash('AWSプロファイルが作成され、デフォルトリージョンおよび出力形式が設定されました', 'success')
        except Exception as e:
            flash(f'AWSプロファイルの作成中にエラーが発生しました: {str(e)}', 'error')

        return redirect(url_for('create_aws_profile'))

    return render_template('testapp/create_aws_profile.html')

@app.route('/tf_exec', methods=['GET'])
@login_required
def tf_exec():
    return render_template('testapp/tf_exec.html')

def format_terraform_output(output):
    # 改行で分割
    lines = output.decode('utf-8').split('\n')
    formatted_lines = []
    for line in lines:
        # ANSIエスケープコードを削除
        line = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', line)
        # 空白を削除してから行を追加
        formatted_lines.append(line.strip())
    
    # 整形された行を連結して整形された出力を生成
    formatted_output = "<p>{}</p>".format('</p><p>'.join(formatted_lines))
    return formatted_output

@app.route('/tf_exec/tf_init', methods=['POST', 'GET'])
@login_required
def tf_init():
    if request.method == 'POST':
        try:
            # terraform initを実行
            init_result = subprocess.run(['terraform', 'init'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Terraform initの出力を整形してファイルに書き込む
            formatted_output = format_terraform_output(init_result.stdout)

            # Terraform initの出力をファイルに書き込む
            with open('/home/vagrant/app2_new/blog/templates/testapp/init_output.html', 'w') as init_output_file:
                init_output_file.write(formatted_output)

            flash('Initが成功しました', 'success')
            return render_template('testapp/tf_init.html')

        except subprocess.CalledProcessError as e:
            # エラーメッセージを整形してファイルに書き込む
            error_output = e.stderr.decode('utf-8')
            formatted_error_output = format_terraform_output(error_output)

            with open('/home/vagrant/app2_new/blog/templates/testapp/init_output.html', 'w') as init_output_file:
                init_output_file.write(formatted_error_output)

            flash('Initに失敗しました。実行結果を確認してください', 'error')
            return render_template('testapp/tf_init.html')
    return render_template('testapp/tf_init.html')

##Terraform Initの実行結果確認
@app.route('/view_init_output')
@login_required
def view_init_output():
    try:
        with open('/home/vagrant/app2_new/blog/templates/testapp/init_output.html', 'r') as init_output_file:
            init_output = init_output_file.read()
        return render_template('testapp/init_output.html', init_output=init_output)
    except FileNotFoundError:
        flash('実行結果ファイルが見つかりません', 'error')
        return redirect(url_for('tf_init'))

UPLOAD_DIR = '/home/vagrant/.ssh/example.pub'

##Terraform Plan 実行機能
@app.route('/tf_exec/tf_plan', methods=['POST', 'GET'])
@login_required
def tf_plan():
    if request.method == 'POST':
        try:
            UPLOAD_DIR = '/home/vagrant/.ssh/'
            public_key = request.form.get('public_key')
            if public_key:
                # セキュアなファイル名を生成して保存
                new_filename = 'example.pub'
                save_path = os.path.join(UPLOAD_DIR, new_filename)
                with open(save_path, 'w') as f:
                    f.write(public_key)

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
        
            # コマンドを実行し、標準出力をバイト文字列として取得
            plan_result = subprocess.run(['terraform', 'plan'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Terraform planの出力を整形してファイルに書き込む
            formatted_output = format_terraform_output(plan_result.stdout)

            # Terraform planの出力をファイルに書き込む
            with open('/home/vagrant/app2_new/blog/templates/testapp/plan_output.html', 'w') as plan_output_file:
                plan_output_file.write(formatted_output)

                flash('Planが成功しました', 'success')
                return render_template('testapp/tf_plan.html')

        except subprocess.CalledProcessError as e:
            # エラーメッセージを整形してファイルに書き込む
            error_output = e.stderr.decode('utf-8')
            formatted_error_output = format_terraform_output(error_output)

            with open('/home/vagrant/app2_new/blog/templates/testapp/plan_output.html', 'w') as plan_output_file:
                plan_output_file.write(formatted_error_output)

            flash('Planに失敗しました。実行結果を確認してください', 'error')
            return render_template('testapp/tf_plan.html')
    return render_template('testapp/tf_plan.html')

##Terraform Planの実行結果確認
@app.route('/view_plan_output')
@login_required
def view_plan_output():
    try:
        with open('/home/vagrant/app2_new/blog/templates/testapp/plan_output.html', 'r') as plan_output_file:
            plan_output = plan_output_file.read()
        return render_template('testapp/plan_output.html', plan_output=plan_output)
    except FileNotFoundError:
        flash('実行結果ファイルが見つかりません', 'error')
        return redirect(url_for('tf_plan'))


##Terraform Apply 実行機能
@app.route('/tf_exec/tf_apply', methods=['POST', 'GET'])
@login_required
def tf_apply():
    if request.method == 'POST':
        try:
            UPLOAD_DIR = '/home/vagrant/.ssh/'
            public_key = request.form.get('public_key')
            if public_key:
                # セキュアなファイル名を生成して保存
                new_filename = 'example.pub'
                save_path = os.path.join(UPLOAD_DIR, new_filename)
                with open(save_path, 'w') as f:
                    f.write(public_key)

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
        
            # コマンドを実行し、標準出力をバイト文字列として取得
            apply_result = subprocess.run(['terraform', 'apply', '-auto-approve'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Terraform Applyの出力を整形してファイルに書き込む
            formatted_output = format_terraform_output(apply_result.stdout)

            # Terraform Apllyの出力をファイルに書き込む
            with open('/home/vagrant/app2_new/blog/templates/testapp/apply_output.html', 'w') as apply_output_file:
                apply_output_file.write(formatted_output)

                flash('Applyが成功しました', 'success')
                return render_template('testapp/tf_apply.html')

        except subprocess.CalledProcessError as e:
            # エラーメッセージを整形してファイルに書き込む
            error_output = e.stderr.decode('utf-8')
            formatted_error_output = format_terraform_output(error_output)

            with open('/home/vagrant/app2_new/blog/templates/testapp/apply_output.html', 'w') as apply_output_file:
                apply_output_file.write(formatted_error_output)

            flash('Applyに失敗しました。実行結果を確認してください', 'error')
            return render_template('testapp/tf_apply.html')
    return render_template('testapp/tf_apply.html')

##Terraform Applyの実行結果確認
@app.route('/view_apply_output')
@login_required
def view_apply_output():
    try:
        with open('/home/vagrant/app2_new/blog/templates/testapp/apply_output.html', 'r') as apply_output_file:
            apply_output = apply_output_file.read()
        return render_template('testapp/apply_output.html', apply_output=apply_output)
    except FileNotFoundError:
        flash('実行結果ファイルが見つかりません', 'error')
        return redirect(url_for('tf_apply'))

##Terraform Destroy 実行機能
@app.route('/tf_exec/tf_destroy', methods=['POST', 'GET'])
@login_required
def tf_destroy():
    if request.method == 'POST':
        try:
            UPLOAD_DIR = '/home/vagrant/.ssh/'
            public_key = request.form.get('public_key')
            if public_key:
                # セキュアなファイル名を生成して保存
                new_filename = 'example.pub'
                save_path = os.path.join(UPLOAD_DIR, new_filename)
                with open(save_path, 'w') as f:
                    f.write(public_key)

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
        
            # コマンドを実行し、標準出力をバイト文字列として取得
            destroy_result = subprocess.run(['terraform', 'destroy', '-auto-approve'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Terraform Applyの出力を整形してファイルに書き込む
            formatted_output = format_terraform_output(destroy_result.stdout)

            # Terraform Apllyの出力をファイルに書き込む
            with open('/home/vagrant/app2_new/blog/templates/testapp/destroy_output.html', 'w') as destroy_output_file:
                destroy_output_file.write(formatted_output)

                flash('Destroyが成功しました', 'success')
                return render_template('testapp/tf_destroy.html')

        except subprocess.CalledProcessError as e:
            # エラーメッセージを整形してファイルに書き込む
            error_output = e.stderr.decode('utf-8')
            formatted_error_output = format_terraform_output(error_output)

            with open('/home/vagrant/app2_new/blog/templates/testapp/destroy_output.html', 'w') as destroy_output_file:
                destroy_output_file.write(formatted_error_output)

            flash('Destroyに失敗しました。実行結果を確認してください', 'error')
            return render_template('testapp/tf_destroy.html')
    return render_template('testapp/tf_destroy.html')

##Terraform Destroyの実行結果確認
@app.route('/view_destroy_output')
@login_required
def view_destroy_output():
    try:
        with open('/home/vagrant/app2_new/blog/templates/testapp/destroy_output.html', 'r') as destroy_output_file:
            destroy_output = destroy_output_file.read()
        return render_template('testapp/destroy_output.html', destroy_output=destroy_output)
    except FileNotFoundError:
        flash('実行結果ファイルが見つかりません', 'error')
        return redirect(url_for('tf_destroy'))
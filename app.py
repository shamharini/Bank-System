from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration (XAMPP defaults)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''   # default for XAMPP is empty
app.config['MYSQL_DB'] = 'bankdb'

mysql = MySQL(app)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Create account
@app.route('/create', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        name = request.form['name']
        initial_balance = float(request.form['balance'])
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO accounts(name, balance) VALUES(%s, %s)", (name, initial_balance))
        mysql.connection.commit()
        cur.close()
        flash('Account created successfully!')
        return redirect(url_for('index'))
    return render_template('create_account.html')

# Deposit
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = float(request.form['amount'])
        cur = mysql.connection.cursor()
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, account_id))
        cur.execute("INSERT INTO transactions(account_id, type, amount) VALUES(%s, 'Deposit', %s)", (account_id, amount))
        mysql.connection.commit()
        cur.close()
        flash('Amount deposited successfully!')
        return redirect(url_for('index'))
    return render_template('deposit.html')

# Withdraw
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = float(request.form['amount'])
        cur = mysql.connection.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id = %s", (account_id,))
        balance = cur.fetchone()[0]
        if balance >= amount:
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, account_id))
            cur.execute("INSERT INTO transactions(account_id, type, amount) VALUES(%s, 'Withdraw', %s)", (account_id, amount))
            mysql.connection.commit()
            flash('Amount withdrawn successfully!')
        else:
            flash('Insufficient balance!')
        cur.close()
        return redirect(url_for('index'))
    return render_template('withdraw.html')

# View balance
@app.route('/balance', methods=['GET', 'POST'])
def balance():
    balance_amount = None
    if request.method == 'POST':
        account_id = request.form['account_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id = %s", (account_id,))
        balance_amount = cur.fetchone()
        if balance_amount:
            balance_amount = balance_amount[0]
        else:
            flash('Account not found!')
        cur.close()
    return render_template('balance.html', balance=balance_amount)

# Transaction history
@app.route('/history', methods=['GET', 'POST'])
def history():
    transactions = []
    if request.method == 'POST':
        account_id = request.form['account_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT type, amount, date FROM transactions WHERE account_id = %s ORDER BY date DESC", (account_id,))
        transactions = cur.fetchall()
        cur.close()
    return render_template('history.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)

import sqlite3 as sql
import os, math
from flask import Flask, render_template,request,session,redirect, url_for
# from flask.ext.session import Session
from flask import url_for
from datetime import datetime,date,timedelta
from werkzeug.utils import secure_filename
import random,uuid

app = Flask(__name__)
app.secret_key = '%jsdj!@'
UPLOAD_FOLDER = 'static/image'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def uniqueid():
    seed = random.randint(1,100000)
    while True:
        yield seed
        seed += 1
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def main():
    if 'username' in session:
        return redirect(url_for('index'))

    return redirect(url_for('login'))
@app.route('/login', methods =['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        validate = validate_user(username,password)
        if validate == False:
            error = 'Invalid credentials. Please try again'
        else:
            session['username'] = username
            return redirect('/index')
    if 'username' in session:
        return redirect('/index')
    return render_template('login.html',error=error)

def validate_user(username,password):
    con = sql.connect('database.db')
    validate = False
    
    with con:
        cur = con.cursor()
        cur.execute('select user_id, password from customer')
        rows = cur.fetchall()
        for row in rows:
            dUser = row[0]
            dPass = row[1]
            if(dUser == username and dPass == password):
                validate = True
    return validate

@app.route('/signup',methods=['GET','POST'])
def signup():
    con = sql.connect('database.db')
    cur = con.cursor()
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        cur.execute('select user_id from customer')
        rows = cur.fetchall()
        for row in rows:
            if(row[0] == username):
                error = 'Username already exist! Try other username'
                return render_template('signup.html',error=error)
        session['username'] = username
        cur.execute("insert into customer values(?,?,?,?)",(username,password,name,email))
        con.commit()
        return redirect('/index')
    if 'username' in session:
        return redirect('/index')
    return render_template('signup.html',error=error)

@app.route('/index', methods=['GET'])
def index():

    if 'username' in session:
        # con = sql.connect('database.db')
        # cur = con.cursor()
        # cur.execute('select * from stock')
        # rows1 = cur.fetchall()
        # cur.execute('select cat_name from category')
        # rows2 = cur.fetchall()
        return redirect('/allStock')
    return redirect('/login')
    

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



@app.route('/myAccount', methods=['GET'])
def myAccount():
    if 'username' in session:
        username = session['username']
        con = sql.connect('database.db')
        cur = con.cursor()
        cur.execute("select user_id,name,email from customer where user_id = (?)",(username,))
        rows = cur.fetchone()
        #rows has user information, logged in
        return render_template('/myAccount.html',rows=rows) #update/change here
    return redirect('/index')

@app.route('/myOrders', methods=['GET'])
def myOrders():
    if 'username' in session:
        username = session['username']
        con = sql.connect('database.db')
        cur = con.cursor()
        cur.execute("select c.name, e.enq_id,e.enq_date, e.cycle_name,g.cat_name,s.sell_price from customer c, enquiry e, category g, stock s where c.user_id = e.user_id and s.cycle_name = e.cycle_name and g.cat_id = e.cat_id and c.user_id = (?)",(username,))
        rows = cur.fetchall()
        return render_template('/myOrders.html',rows=rows) #update/change here
    return redirect('/index')



#---------------------------------------ADMIN PRIORITIES-------------------------------------

@app.route('/addStock',methods = ['GET','POST'])
def addStock():
    con = sql.connect('database.db')
    duplicate = False
    msg = None
    if(request.method == 'POST'):
        cycle_name = request.form['cycle_name']
        cat_id = request.form['cat_id']
        cost_price = request.form['cost_price']
        quantity = request.form['quantity']
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        duplicate = duplicate_stock(cycle_name)
        if(duplicate == True):
            msg = 'Cycle already in stock'
            return render_template('addStock.html',msg = msg)
        cur = con.cursor()
        cur.execute("insert into stock(cycle_name,cat_id,cost_price,cycle_image,quantity) values(?,?,?,?,?)",(cycle_name,cat_id,cost_price,imagename,quantity))
        con.commit()
        msg = "Stock added successfully"
        return render_template('addStock.html',msg=msg)
    return render_template('addStock.html')
def duplicate_stock(cycle_name):

    con = sql.connect('database.db')
    duplicate = False
    
    with con:
        cur = con.cursor()
        cur.execute('select cycle_name from stock')
        rows = cur.fetchall()
        for row in rows:
            dCycle = row[0]
            if(dCycle == cycle_name):
                duplicate = True
                break
    return duplicate



@app.route('/adminLogin', methods=['GET','POST'])
def adminLogin():
    msg = None
    if 'username' in session:
        return redirect('/index')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if (username == 'vikash' and password == 'vikash1234'):
            return redirect('/addStock')
        else:
            msg = "Invalid credentials! Try again!"
            return render_template('adminLogin.html',msg=msg)
    return render_template('adminLogin.html')

# ------------------PAGES TO BE UPDATED--------------------------
# @app.route('/suppliers')
# def suppliers():
#     con = sql.connect('database.db')
#     cur = con.cursor()
#     cur.execute("select * from suppliers")
#     rows = cur.fetchall()
#     #rows-> all supplier data

# @app.route('/suppliedCycles')
# def suppliedCycles():
#     #selected_supplier
#     con = sql.connect('database.db')
#     cur = con.cursor()
#     cur.execute("select p.cycle_name from suppliers s, supplies p where s.s_id = p.s_id and s_id = (?)",(selected_supplier,))
#     rows = cur.fetchall()
#     #rows->list of cycles by a selected supplier

# @app.route('/allRequests')
# def allRequests():

#     con = sql.connect('database.db')
#     cur = con.cursor()
#     cur.execute("select e.*,c.name,c.email from enquiry e, customer c where c.user_id = e.user_id") 
#     rows = cur.fetchall()
#     #rows-> shows all the incoming requests from any user

@app.route('/allStock', methods=['GET','POST'])
def allStock():
    if 'username' in session:
        con = sql.connect('database.db')
        cur = con.cursor()   
        # cur.execute('select cat_name from category')
        # rows1 = cur.fetchall()
        cat_name = request.args.get('cat')
        if(cat_name):
            # cat_name = request.form['category']
            
            cur.execute("select s.* from stock s, category c where s.cat_id = c.cat_id and c.cat_name = (?)",(cat_name,))
            rows = cur.fetchall()
            return render_template('/allStock.html', rows=rows)
        cur.execute("select s.* from stock s, category c where s.cat_id = c.cat_id and c.cat_name = 'boys'")
        rows = cur.fetchall()
        return render_template('/allStock.html', rows=rows)   
    return redirect('/index')

@app.route('/enquiry')
def enquiry():
    if 'username' in session:
        username = session['username']
        con = sql.connect('database.db')
        cur = con.cursor()
        cycle_name = request.args.get('cycle')
        cat_id = request.args.get('cat')
        enq_id = str(uniqueid())
        d_a_t_e=(datetime.now().date())
        cur.execute("select cat_name from category where cat_id = (?)",(cat_id,))
        cat_name = cur.fetchone()
        cur.execute("insert into enquiry values (?,?,?,?,?)",(enq_id,username,cycle_name,cat_id,d_a_t_e))
        con.commit()
        msg = "Enquiry placed! Check on My Orders"
        return redirect(url_for('allStock', cat=cat_name))
        
    return redirect('/index')

if __name__ == "__main__":
    app.run(debug = True)
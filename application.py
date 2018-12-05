import sqlite3 as sql
import os, math
from flask import Flask, render_template,request,session,redirect, url_for, flash
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
admin = "vikash"
passWord = "vikash1234"

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
        if (session['username'] == admin):
            return redirect('/adminPage')
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
        ph_no = request.form['ph_no']
        cur.execute('select user_id from customer')
        rows = cur.fetchall()
        for row in rows:
            if(row[0] == username):
                error = 'Username already exist! Try other username'
                return render_template('signup.html',error=error)
        session['username'] = username
        cur.execute("insert into customer values(?,?,?,?)",(username,password,name,ph_no))
        con.commit()
        return redirect('/index')
    if 'username' in session:
        return redirect('/index')
    return render_template('signup.html',error=error)

@app.route('/index', methods=['GET'])
def index():
    
    if 'username' in session:
        if (session['username'] == admin):
            return redirect('/adminPage')
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
        cur.execute("select user_id,name,ph_no from customer where user_id = (?)",(username,))
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
    if 'username' in session:
        if (session['username'] == admin):
            con = sql.connect('database.db')
            cur = con.cursor()
            duplicate = False
            msg = None
            if(request.method == 'POST'):
                cycle_name = request.form['cycle_name']
                cat_id = request.form['cat_id']
                s_id = request.form['s_id']
                cost_price = request.form['cost_price']
                quantity = request.form['quantity']
                image = request.files['image']
                description = request.form['description']
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagename = filename
                duplicate = duplicate_stock(cycle_name)
                if(duplicate == True):
                    msg = 'Cycle already in stock'
                    return render_template('addStock.html',msg = msg)
                
                cur.execute("insert into stock(cycle_name,cat_id,cost_price,cycle_image,quantity,description) values(?,?,?,?,?,?)",(cycle_name,cat_id,cost_price,imagename,quantity,description))
                con.commit()
                cur.execute("insert into supplies values(?,?)",(s_id,cycle_name,))
                con.commit()
                msg = "Stock added successfully" 
                cur.execute("select * from category")
                rows1 = cur.fetchall()
                cur.execute("select * from suppliers")
                rows2 = cur.fetchall()
                return render_template('addStock.html',rows1=rows1,rows2=rows2)
            cur.execute("select * from category")
            rows1 = cur.fetchall()
            cur.execute("select * from suppliers")
            rows2 = cur.fetchall()
            return render_template('addStock.html',rows1=rows1,rows2=rows2)
    return redirect('/index')
    
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

        if (username == admin and password == passWord):
            session['username'] = username
            return redirect('/adminPage')
        else:
            msg = "Invalid credentials! Try again!"
            return render_template('adminLogin.html',msg=msg)
    return render_template('adminLogin.html')


@app.route('/allStock', methods=['GET','POST'])
def allStock():
    if 'username' in session:
        username = session['username']
        con = sql.connect('database.db')
        cur = con.cursor()   
        cur.execute("select e.enq_date, e.cycle_name, c.cat_name, s.sell_price from enquiry e, stock s, category c where e.cycle_name = s.cycle_name and e.cat_id = c.cat_id and e.user_id = (?)",(username,))
        rows1 = cur.fetchall()
        cat_name = request.args.get('cat')
        if(cat_name):
            cur.execute("select s.* from stock s, category c where s.cat_id = c.cat_id and c.cat_name = (?)",(cat_name,))
            rows = cur.fetchall()
            return render_template('/allStock.html', rows=rows,rows1=rows1)
        cur.execute("select s.* from stock s, category c where s.cat_id = c.cat_id and c.cat_name = 'boys'")
        rows = cur.fetchall()
        return render_template('/allStock.html', rows=rows,rows1=rows1)   
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
        flash('Enquiry places successfully!')
        return redirect(url_for('allStock', cat=cat_name))
        
    return redirect('/index')

@app.route('/adminPage')
def adminPage():
    if 'username' in session:
        if (session['username'] == admin):
            con = sql.connect('database.db')
            cur = con.cursor()  
            cur.execute("select s.cycle_name,c.cat_name,s.cost_price,s.sell_price,s.quantity,sup.s_name from stock s, suppliers sup, supplies ss, category c where s.cat_id=c.cat_id and s.cycle_name=ss.cycle_name and ss.s_id=sup.s_id")
            # cur.execute('select * from stock')
            rows = cur.fetchall()
            cur.execute("select * from suppliers")
            rows1=cur.fetchall()
            cur.execute("select e.user_id,c.name, e.cycle_name, cg.cat_name, e.enq_date,c.ph_no from enquiry e, category cg, customer c  where e.cat_id=cg.cat_id and e.user_id=c.user_id")
            rows2=cur.fetchall()
            return render_template('adminPage.html',rows=rows, rows1=rows1, rows2=rows2)        
    return redirect('/index')

@app.route('/updateStock', methods=['GET','POST'])
def updateStock():
    if 'username' in session:
        if(session['username'] == admin):
            con = sql.connect('database.db')
            cur = con.cursor() 
            if (request.method == 'GET'):
                cycle_name = request.args.get('cycle_name')
                cur.execute("select s.*,sup.s_id from stock s, supplies sup where s.cycle_name = sup.cycle_name and s.cycle_name = (?)",(cycle_name,)) 
                rows = cur.fetchall()
                cur.execute("select * from category")
                rows1 = cur.fetchall()
                cur.execute("select * from suppliers")
                rows2 = cur.fetchall()
                return(render_template('/updateStock.html', rows=rows,rows1=rows1,rows2=rows2))

            cycle_name = request.form['cycle_name']
            cat_id = request.form['cat_id']
            s_id = request.form['s_id']
            cost_price = request.form['cost_price']
            quantity = request.form['quantity']
            try:
                image = request.files['image']
            except KeyError:
                image=None
            description = request.form['description']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            if(image):
                imagename = filename
                cur.execute("update stock set cat_id =(?),cost_price=(?),quantity=(?),cycle_image=(?),description=(?) where cycle_name=(?)",(cat_id,cost_price,quantity,imagename,description,cycle_name,))
                con.commit()
            elif(image is None):
                cur.execute("update stock set cat_id =(?),cost_price=(?),quantity=(?),description=(?) where cycle_name=(?)",(cat_id,cost_price,quantity,description,cycle_name,))
                con.commit()    
            
            cur.execute("update supplies set s_id = (?) where cycle_name = (?)",(s_id,cycle_name,))
            con.commit()
            return(redirect(url_for('adminPage')))
        
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/addSupplier',methods = ['GET','POST'])
def addSupplier():
    if 'username' in session:
        if (session['username'] == admin):
            con = sql.connect('database.db')
            cur = con.cursor()
            duplicate = False
            msg = None
            cur.execute("select * from suppliers")
            rows = cur.fetchall()
            if(request.method == 'POST'):

                s_id = request.form['s_id']
                s_name = request.form['s_name']
                s_city = request.form['s_city']
                ph_no = request.form['ph_no']
                email = request.form['email']

                duplicate = duplicate_supplier(s_id)
                if(duplicate == True):
                    msg = 'Supplier id already exist!'
                    return render_template('addSupplier.html',msg = msg,rows=rows)
                
                cur.execute("insert into suppliers values(?,?,?,?,?)",(s_id,s_name,s_city,ph_no,email))
                con.commit()
                msg = "Supplier added successfully"
                cur.execute("select * from suppliers")
                rows = cur.fetchall()
                return render_template('addSupplier.html',msg=msg,rows=rows)

            return render_template('addSupplier.html',rows=rows)
        return redirect('/index')
    return redirect('/index')
    
def duplicate_supplier(s_id):

    con = sql.connect('database.db')
    duplicate = False
    
    with con:
        cur = con.cursor()
        cur.execute('select s_id from suppliers')
        rows = cur.fetchall()
        for row in rows:
            sup_id = row[0]
            if(sup_id == s_id):
                duplicate = True
                break
    return duplicate

@app.route('/deleteStock', methods=['GET','POST'])
def deleteStock():
    if 'username' in session:
        if(session['username'] == admin):
            msg = None
            con = sql.connect('database.db')
            cur = con.cursor()
            cycle_name = request.args.get('cycle_name')
            cur.execute("delete from stock where cycle_name = (?)",(cycle_name,))
            con.commit()
            msg = "Cycle deleted successfully from database"
            return redirect(url_for('adminPage', msg=msg))
        return redirect('/index')
    return redirect('/index')
if __name__ == "__main__":
    app.run(debug = True)
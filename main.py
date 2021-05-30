from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from sendemail import email_alert
import io
import xlwt
import pymysql

app = Flask(__name__)

app.secret_key = 'a'

# database connection details
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = '8GTABQ1kXu'
app.config['MYSQL_PASSWORD'] = 'jCJoTT72Ji'
app.config['MYSQL_DB'] = '8GTABQ1kXu'

# Intialize MySQL
mysql = MySQL(app)

# SignUp Code (start)
@app.route('/', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form :
        username = request.form['username']
        email = request.form['email']
        session["email"] = email
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, email, password ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template ('login.html')
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)
# SignUp Code (End)
#--------------------------------------------------------------------------------------------------------------------------------------#
# Login Code (Start)
@app.route('/login', methods=['GET','POST'])
def login():
    global email
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = % s AND password = % s AND username = % s', (email, password, username ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['username'] = account['username']
            msg = username
            return render_template('home.html', msg = msg)
        else:
            msg = 'Incorrect email / password !'
    return render_template('login.html', msg = msg)
# Login Code (end)
#--------------------------------------------------------------------------------------------------------------------------------------#
# Home Page Code (START)
@app.route('/home')
def home():
    if "username" in session:
        username = session['username']
        return render_template('home.html',msg = username)
    else:
        return redirect(url_for("login"))
# Home Page Code (end)
#--------------------------------------------------------------------------------------------------------------------------------------#
# STOCK page code (START)
@app.route("/stockbalance")
def stockbalance():
    if "username" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from Products")
   
        rows = cursor.fetchall();
        username = session['username']
        return  render_template('stock.html',rows = rows, msg = username) 
    else:
        return redirect(url_for("login"))
# STOCK page code (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# Product Page Code (Start)
@app.route('/product')
def product():
    if "username" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from Products")
        rows = products = cursor.fetchall()
        username = session['username']
        return render_template('Product.html',rows = rows, msg = username)
    else:
        return redirect(url_for("login"))
# Product Page Code (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
#ADD Product Code (Start)
@app.route('/addProduct',methods = ['POST','GET'])
def addProduct():
   if request.method == 'POST':
      try:
         productname = request.form['pn']
         productdescription = request.form['pd']
         productqty = request.form['pq']
         cursor = mysql.connection.cursor()
         cursor.execute('INSERT INTO Products VALUES (NULL, % s, % s, % s)',(productname, productdescription, productqty))
         mysql.connection.commit()
         flash('New Product Added')
         msg = "Record added"
         cursor.close()
      except: 
         msg = "error in  operation"
      
      finally:
         return  redirect(url_for('product',msg=msg))
#ADD Product Code (end)
#--------------------------------------------------------------------------------------------------------------------------------------#
#EDIT Product code (START)     
@app.route('/editProduct',methods = ['POST'])
def editProduct():
   if request.method == 'POST' and 'ProductID' in request.form and 'NEWProductName' in request.form and 'NEWProductDescription' in request.form and 'NEWProductQty':
      try:
         productID = request.form['ProductID']
         productName = request.form['NEWProductName']
         productDescription=request.form['NEWProductDescription']
         ProductQty=request.form['NEWProductQty']
         zero = "0"
         msg = "Product Edited "
         
         if ProductQty == zero:
             email = session["email"]
             cursor = mysql.connection.cursor()
             email_alert (email)
             flash('The Stock Alert Message Has been Sent')
             cursor.execute("UPDATE Products SET QTY = % s WHERE productID = % s",(ProductQty,productID))
             mysql.connection.commit()
             cursor.close()
             return  redirect(url_for('product'))
         else:
             cursor = mysql.connection.cursor()
             flash('Product Edited')
             cursor.execute("UPDATE Products SET productName = % s,productDescription = % s, QTY = % s WHERE productID = % s",(productName,productDescription,ProductQty,productID) )
             mysql.connection.commit()
             cursor.close()
             return "Product Edited. Please press back.";
      except:
             msg = "error in operation"
      finally:
         #return "product edited"
         return  redirect(url_for('product',msg=msg))
# EDIT Product code (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# Delete Product CODE (start)        
@app.route('/deleteProduct/<productID>')
def deleteProduct(productID):
      try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM Products WHERE productID = % s",(productID,))
            
            mysql.connection.commit()
            flash('Product Deleted')
            msg = "Product Deleted"
      except:
            msg = "error in operation"
   
      finally:
            return  redirect(url_for('product',msg=msg))
            cursor.close()
# Delete Product CODE (END)  
#--------------------------------------------------------------------------------------------------------------------------------------#    
# Location Page CODE (START)
@app.route("/location")
def Location():
  if "username" in session:
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute("select * from Locations")
   mysql.connection.commit()
   rows = cursor.fetchall()
   username = session['username']
   return  render_template('Location.html',rows = rows, msg = username) 
  else:
     return redirect(url_for("login"))
# Location Page CODE (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# ADD Locations CODE (START)
@app.route('/addlocation',methods = ['POST'])
def addlocation():
   if request.method == 'POST':
      try:
         ln = request.form['ln']

         cursor = mysql.connection.cursor()
         cursor.execute("INSERT INTO Locations (locationName) VALUES (% s)",(ln,))
         flash('New Location Added')
         mysql.connection.commit()
         msg = "successfully added"
      except:
            msg = "error in operation"
      
      finally:
            return  redirect(url_for('Location',msg=msg))
            cursor.close()
# ADD Locations CODE (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# Edit Location CODE (START)
@app.route('/editlocation',methods = ['POST'])
def editlocation():
   if request.method == 'POST':
      try:
         locationID = request.form['locationID']
         locationName = request.form['NEWLocationName']
         cursor = mysql.connection.cursor()
         cursor.execute("UPDATE Locations SET LocationName = % s WHERE LocationID = % s",(locationName,locationID) )
         flash('Location Edited')
         mysql.connection.commit()
         msg = "location Edit Successfully"
      except:
         msg = "error operation"
      
      finally:
         return  redirect(url_for('Location',msg=msg))
         cursor.close()
# Edit Location CODE (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# Delete Location CODE (START)
@app.route('/deletelocation/<locationID>')
def deletelocation(locationID):
      try:
          cursor = mysql.connection.cursor()
          cursor.execute("DELETE FROM Locations WHERE LocationID = % s ",(locationID))
          flash('Location Deleted')
          mysql.connection.commit()
          msg = "location Delete Successfully"
      except:
            msg = "error operation"
   
      finally:
            return  redirect(url_for('Location',msg=msg))
            cursor.close()
# Delete Location CODE (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# pRODUCT mOVEMENT CODE (START)
@app.route('/productmovement')
def ProductMovement():
 if "username" in session:
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute("select * from Product_movement")
   
   rows = cursor.fetchall()

   cursor.execute("select * from Products")
   productRows = cursor.fetchall()

   cursor.execute("select * from Locations")
   locationRows = cursor.fetchall()

   for pr in productRows:
      for lr in locationRows:
         cursor.execute("SELECT * FROM Balance WHERE LocationName = % s AND ProductName = % s ",(lr["LocationName"],pr["ProductName"]))
         data = cursor.fetchall()

         if len(data) == 0:
            cursor.execute("INSERT INTO Balance (LocationName, ProductName, qty)VALUES (% s,% s,% s)",(lr["LocationName"],pr["ProductName"],0))
            mysql.connection.commit()
   username = session['username']
   return render_template('ProductMovement.html',rows = rows,  productRows = productRows, locationRows = locationRows, msg = username)
   cursor.close()
 else:
     return redirect(url_for("login"))
# pRODUCT mOVEMENT CODE (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# ADD ProductMovement CODE (START)
@app.route('/addProductMovement',methods = ['POST'])
def addProductMovement():
   if request.method == 'POST':
      try:
         pn = request.form['pn']
         datetime = request.form['datetime']
         fromlocation = request.form['fromlocation']
         tolocation = request.form['tolocation']
         pq =request.form['pq']
        
         
         cursor = mysql.connection.cursor()
         cursor.execute("INSERT INTO Product_movement (ProductName,Timing,fromlocation,tolocation,QTY) VALUES (% s,% s,% s,% s,% s)",(pn,datetime,fromlocation,tolocation,pq) )
         flash('Product Movement Added')
         mysql.connection.commit()
         msg = "Record added"
      except:
         msg = "error in  operation"
      
      finally:
          return  redirect(url_for('ProductMovement',msg=msg))
          cursor.close()
# ADD ProductMovement CODE (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# Edit ProductMovement CODE (START) 
@app.route('/editProductMovement',methods = ['POST'])
def editProductMovement():
   if request.method == 'POST':
      try:
         movementID = request.form['movementID']
         ProductName = request.form['NEWProductName']
         datetime = request.form['NEWDateTime']
         fromlocation = request.form['NEWfromlocation']
         tolocation = request.form['NEWtolocation']
         qty=request.form['NEWProductQty']
         cursor = mysql.connection.cursor()
         cursor.execute("UPDATE Product_movement SET ProductName = % s,Timing = % s,fromlocation = % s,tolocation = % s,QTY = % s WHERE movementID = % s",(ProductName,datetime,fromlocation,tolocation,qty,movementID),)
         flash('Product Movement Edited')
         mysql.connection.commit()
         msg = " movement Edit Successfully"
      except:
         msg = "error operation"
      
      finally:
         return  redirect(url_for('ProductMovement',msg=msg))
         cursor.close()
# Edit ProductMovement CODE (END) 
#--------------------------------------------------------------------------------------------------------------------------------------#
# Delete Product Movement CODE (START)
@app.route('/deleteprouctmovement/<movementID>')
def deleteprouctmovement(movementID):
      try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM Product_movement WHERE movementID = % s ",(movementID))
            flash('Product Movement Deleted')
            mysql.connection.commit()
            msg = "movement Delete Successfully"
      except:
            msg = "error operation"
   
      finally:
            return  redirect(url_for('ProductMovement',msg=msg))
            cursor.close()
# Delete Product Movement CODE (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
# EXPORT CODE (START)
@app.route('/download/report/excel')
def download_report():
		cursor = mysql.connection.cursor()
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		
		cursor.execute("SELECT ProductID, ProductName, ProductDescription, QTY FROM Products")
		result = cursor.fetchall()
		
		#output in bytes
		output = io.BytesIO()
		#create WorkBook object
		workbook = xlwt.Workbook()
		#add a sheet
		sh = workbook.add_sheet('Stock Products')
		
		#add headers
		sh.write(0, 0, 'Product Id')
		sh.write(0, 1, 'Product Name')
		sh.write(0, 2, 'Product Description')
		sh.write(0, 3, 'QTY')
		
		idx = 0
		for row in result:
			sh.write(idx+1, 0, str(row['ProductID']))
			sh.write(idx+1, 1, row['ProductName'])
			sh.write(idx+1, 2, row['ProductDescription'])
			sh.write(idx+1, 3, row['QTY'])
			idx += 1
		
		workbook.save(output)
		output.seek(0)
		
		return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=Stock_products.xls"})
# export code (closed)
#--------------------------------------------------------------------------------------------------------------------------------------#
# Logout CODE (START)
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('login.html')
# LOGOUT CODE (END)
#--------------------------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
   app.run(host ='0.0.0.0', port = 8080, debug = True)
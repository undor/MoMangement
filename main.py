from flask import Flask ,request ,redirect
from flask import render_template
import garden_db
import sqlite3 as sql
import logging
import os
from google.cloud import storage


## the Flask APP and the Google Cloud storage initiation
app = Flask(__name__)
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']


"""
Upload method.
uploads the reqested filw to the cloud
"""
def upload(uploaded_file):
    if not uploaded_file:
        return 'No file uploaded.', 400

    gcs = storage.Client()

    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(uploaded_file.filename)

    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )

    return blob.public_url


"""
handles server errors
"""
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


"""
the root homepage
show the years currently in the system
"""
@app.route("/")
def root():
    con = sql.connect(garden_db.db_location)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from kindergardens")
    gardens = cur.fetchall()
    cur.execute("SELECT DISTINCT year FROM recepts")
    years = cur.fetchall()
    return render_template("index.html",items=gardens,years = years)

"""
Year Page
show  a table of gardens and months 
"""
@app.route("/<year>")
def year_page(year):
    con = sql.connect(garden_db.db_location)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select DISTINCT name from kindergardens")
    gardens_name = cur.fetchall()
    final_table=[]
    for i in range(len(gardens_name)):
        cur.execute("SELECT  * from recepts WHERE (year= "+ year + " AND  kindergarden='"+ gardens_name[i][0]+ "')")
        recepts = cur.fetchall()
        final_table.append([0] *12)
        for line in recepts:
            cur_month=line["month"]-1
            final_table[i][cur_month]=1
    return render_template("year.html",items=gardens_name,year= year,table=final_table,ids=gardens_name)

"""
Year Page
show data for a garden in specefic year
"""
@app.route("/<garden>/<year>")
def garden_page(garden,year):
    con = sql.connect(garden_db.db_location)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT  * from recepts WHERE (year= "+ year + " AND  kindergarden='"+ garden+ "')")
    garden_recepts = cur.fetchall()
    return render_template("garden.html",items=garden_recepts ,year= year,garden=garden)

"""
Accpeting new garden
this method adds a new garden andd redirect back to the relevant year
"""    
@app.route('/res_page',methods = ['POST', 'GET'])
def res_page():
    if request.method == 'POST':
        con = sql.connect(garden_db.db_location)
        cur = con.cursor()      

        year = request.form['year']
        name = request.form['garden']
        addr = request.form['location']
        payment=request.form['payment']
        
        cur.execute("INSERT INTO kindergardens (name,pay_method,city) VALUES (?,?,?)",(name,payment,addr) )
        con.commit()
        con.close()
        return year_page(year)

"""
Accpeting new recept
this method adds a new recept andd redirect back to the relevant year
"""                
@app.route('/res_page_recept',methods = ['POST', 'GET'])
def res_page_recept():
    if request.method == 'POST':
        con = sql.connect(garden_db.db_location)
        cur = con.cursor()      
        garden = request.form['garden']
        year = request.form['year']
        month = request.form['month']
        date = request.form['date']
        amount=request.form['amount']
        img_url= upload(request.files.get('file'))
        cur.execute("INSERT INTO recepts (kindergarden,month,year,status,payment_day,img_url,amount) VALUES (?,?,?,?,?,?,?)",(garden,month,year,"payed",date,img_url,amount) )
        con.commit()

        con.close()
        return year_page(year)
            
            
"""
Recept page
Showing information of a specific page
"""     
@app.route("/<year>/<garden>/<month>")
def recept_page(garden,year,month):
    con = sql.connect(garden_db.db_location)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select *  from recepts WHERE year="+ year+" AND month = "+ month+" AND kindergarden='"+ garden+"'")
    info = cur.fetchall()
    cur.execute("select DISTINCT name from kindergardens WHERE name='"+ garden+"'")
    garden_n=cur.fetchall()
    if len(info)==0 :
        return "not exist!" + garden_n + " " + year + " " + month
    con.close()
    return render_template("recept.html",garden_name=garden_n[0][0],year= year,month=int(month)+1, info=info)

"""
Delete recept
delete recept and redirect back to relevant year

"""     
@app.route("/delete_recept/<year>/<recept_id>")
def delete_recept(recept_id,year):
    con = sql.connect(garden_db.db_location)
    cur = con.cursor()
    cur.execute(" DELETE FROM recepts WHERE id =" +  recept_id)
    con.commit()
    return redirect("/"+year, code=302)
    
if __name__ == '__main__':
    garden_db.init_db(garden_db.db_location)
    #app.run(host='127.0.0.1', debug=True)
    app.run(host='0.0.0.0', port=8080, debug=True)
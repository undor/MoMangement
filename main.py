from flask import Flask ,request
from flask import render_template
import garden_db
import sqlite3 as sql

app = Flask(__name__)



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
        cur.execute("INSERT INTO recepts (kindergarden,month,year,status,payment_day,img_url,amount) VALUES (?,?,?,?,?,?,?)",(garden,month,year,"payed",date,"4543",amount) )
        con.commit()

        con.close()
        return year_page(year)
            

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
    return render_template("recept.html",garden_name=garden_n[0][0],year= year,month=int(month)+1, info=info)


@app.route("/delete_recept/<recept_id>")
def delete_recept(recept_id):
    con = sql.connect(garden_db.db_location)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("DELETE   from recepts WHERE id = " +recept_id)
    return root()
    
if __name__ == '__main__':
    garden_db.init_db(garden_db.db_location)
    app.run(host='127.0.0.1', debug=True)
#    app.run(host='0.0.0.0', port=8080, debug=True)
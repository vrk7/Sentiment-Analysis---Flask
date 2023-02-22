from flask import Flask, render_template, request
from preprocess import *
import sqlite3 as sql

# Creating a Flask Object
app=Flask('__name__')

# Declare global variables to store user review and predicted sentiment
global reviews
global predictions

# Define route to handle form submissions and home page
@app.route('/',methods=['GET'])
@app.route('/submit',methods=['GET','POST'])
def home_page():
    global reviews,predictions

    # If form is submitted with POST method, extract review, predict sentiment and store in database
    if request.method=='POST':
        og_review=request.form['review']
        predictor=analyse(str(og_review))
        review=predictor.prediction 
        reviews=og_review
        predictions=review

        # Connect to database, insert review and its sentiment, and commit changes
        with sql.connect('database.db') as connection:
            cursor=connection.cursor()
            cursor.execute("INSERT INTO reviews (review,sentiment) VALUES (?,?)",(og_review,review))
            connection.commit()

        # Render result.html template with predicted sentiment passed as parameter
        return render_template('result.html',review=review)

    # If request method is GET, render hello.html template
    return render_template('hello.html')
        
# Define route to display data from the database
@app.route('/data')
def database():
    # Connect to database, select all rows from reviews table, fetch them and close connection
    connection=sql.connect('database.db')
    connection.row_factory=sql.Row

    cursor=connection.cursor()
    cursor.execute('select * from reviews')

    rows=cursor.fetchall()
    connection.close()

    # Render data.html template with rows passed as parameter
    return render_template('data.html',rows=rows)

# Define route to update status of reviews that are correctly labeled
@app.route('/updatefalse',methods=['GET','POST'])
def update_true():
    global reviews

    # If request method is GET, update status of review in database as "True" (correctly labeled)
    if request.method=='GET':
        with sql.connect('database.db') as connection:
            cursor=connection.cursor()
            cursor.execute('UPDATE reviews SET status="True" WHERE review="'+str(reviews)+'"')
            connection.commit()

    # Render hello.html template
    return render_template('hello.html')        

# Define route to update status of reviews that are incorrectly labeled
@app.route('/updatetrue',methods=['GET','POST'])
def update_false():
    global reviews,predictions

    # If request method is GET, update status of review in database as "False" (incorrectly labeled)
    if request.method=='GET':
        print(reviews,predictions)  
        with sql.connect('database.db') as connection:
            cursor=connection.cursor()
            cursor.execute('UPDATE reviews SET status="False" WHERE review="'+str(reviews)+'"')
            connection.commit()

    # Render hello.html template
    return render_template('hello.html')


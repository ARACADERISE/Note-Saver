from flask import Flask, render_template


class Webpage:

    APP = Flask(__name__)

    def __init__(self, database, port_database):
        self.db = database
        self.PortDb = port_database

    @APP.route('/')
    def startup_webpage():
        return render_template('homepage.html')
    
    APP.run(debug=True)

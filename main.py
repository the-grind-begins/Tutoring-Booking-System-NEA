from website import create_app

app = create_app()

if __name__ == '__main__': #any change made in python file will be updated in the webserver
    app.run(debug=True) #if you want to import main.py from another place this stops it

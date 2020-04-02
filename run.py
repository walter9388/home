# import app from wherever
from heroku import heroku_dash_example
# from plotting_stuff import example_dash

# run file like so
app = heroku_dash_example.run_me()
server = app.server
# example_dash.heroku_call()

if __name__ == '__main__':
    app.run_server(debug=True)

# from heroku import flaskapp
# if __name__ == '__main__':
#     flaskapp.run(debug=True)
# import app from wherever
from heroku import heroku_dash_example
from plotting_stuff import example_dash

# for running flash
from plotting_stuff import qtwidge

# get app
# app = heroku_dash_example.run_me()
app = example_dash.heroku_call()

# get server
server = app.server # if dash

if __name__ == '__main__':
    qtwidge.run_dash(app)

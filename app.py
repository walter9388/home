# import app from wherever
from heroku import heroku_dash_example
# from plotting_stuff import example_dash

if __name__ == '__main__':
    # run file like so
    app = heroku_dash_example.run_me()
    # example_dash.heroku_call()

    app.run_server(debug=True)
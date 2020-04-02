# import app from wherever
from heroku import heroku_dash_example
from plotting_stuff import example_dash, example_panel, example_bokehflask

# for running flash
# from plotting_stuff import qtwidge

# get app
# app = heroku_dash_example.run_me()
# app = example_dash.heroku_call()
# app = example_bokehflask.heroku_call()

# app = heroku_dash_example.heroku_call()

# get server
# server = app.server # if dash
# server = app # if bokeh/panel
# app.debug = True
# app.run()

# pn = example_panel.heruko_call()





import panel as pn

pn.extension('vega')


#######


import altair as alt
from vega_datasets import data

cars = data.cars()

chart = alt.Chart(cars).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).properties(width='container', height='container').interactive()

altair_pane = pn.panel(chart)


# if __name__ == '__main__':
    # qtwidge.run_dash(app)
    # app.run_server(debug=True)

    # app.run()
altair_pane.servable()
    # app.debug = True
    # def run_bokeh(app):
    #     app.run(port=8000)
    # import threading
    # threading.Thread(target=run_bokeh, args=(app,), daemon=True).start()

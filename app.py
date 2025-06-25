import dash
from components.layout import layout
from components.callbacks import register_callbacks

app = dash.Dash(__name__, assets_folder="assets")
app.title = "Dashboard"
app.layout = layout

# wire up all your callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)
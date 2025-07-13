import dash
from components.layout import layout
from components.callbacks.callbacks import register_callbacks

app = dash.Dash(__name__, assets_folder="assets", suppress_callback_exceptions=True)
app.title = "AEID"
app.layout = layout
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
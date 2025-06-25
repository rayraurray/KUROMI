import dash
from components.pages.dashboard import dashboard
from components.callbacks import register_callbacks

app = dash.Dash(__name__, assets_folder="assets")
app.title = "Dashboard"
app.layout = dashboard

# wire up all your callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)
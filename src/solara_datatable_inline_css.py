import solara
import pandas as pd

# Sample data
data = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Country": ["USA", "Canada", "UK"],
})

@solara.component
def Page():
    style = {
        "border": "1px solid #ccc",
        "borderRadius": "8px",
        "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.1)",
        "padding": "10px",
    }

    solara.Markdown("# Styled Table")
    with solara.Div(style=style):
        solara.DataFrame(data)

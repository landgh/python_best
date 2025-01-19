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
    solara.HTML(tag="link", attributes={"rel": "stylesheet", "href": "/static/df.css"})

    solara.Markdown("# Styled Table")
    with solara.Div(style="styled-div"):
        solara.DataFrame(data)

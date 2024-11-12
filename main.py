from fasthtml.common import (
    FastHTML,
    serve,
    Html,
    P,
    Head,
    Title,
    Body,
    Button,
    Input,
    Div,
    H1,
    H2,
    H3,
    H4,
    H5,
    H6,
    Ul,
    Li,
    A,
    Hr,
    Br,
    P,
    Img,
    Form,
    Main,
    picolink,
)


app = FastHTML(hdrs=picolink)
rt = app.route

messages = ["This is a message, which will get rendered as a paragraph"]


@app.get("/")
def home():
    page = Main(
        H1("Messages"),
        *[P(msg) for msg in messages],
        A("Link to Page 2 (to add messages)", href="/page2"),
    )
    return page


@app.get("/page2")
def page2():
    return Main(
        P("Add a message with the form below:"),
        Form(
            Input(type="text", name="data"), Button("Submit"), action="/", method="post"
        ),
    )


@app.post("/")
def add_message(data: str):
    messages.append(data)
    return home()


serve()

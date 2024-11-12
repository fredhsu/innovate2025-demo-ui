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
import yaml
import os
from dataclasses import dataclass


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


@dataclass
class VNIEntry:
    id: str
    vni_override: str
    name: str
    tags: str

@app.get("/yaml-form")
def yaml_form():
    return Main(
        H1("VNI Entry Form"),
        Form(
            Div(
                Input(type="text", name="id", placeholder="ID", required=True),
                Input(type="text", name="vni_override", placeholder="VNI Override", required=True),
                Input(type="text", name="name", placeholder="Name", required=True),
                Input(type="text", name="tags", placeholder="Tags (comma-separated)", required=True),
            ),
            Button("Submit", type="submit"),
            action="/save-yaml", 
            method="post"
        )
    )

@app.post("/save-yaml")
def save_yaml(entry: VNIEntry):
    # Read the existing YAML file
    with open("TENANTS.yaml", 'r') as f:
        tenants_data = yaml.safe_load(f)
    
    # Prepare the new L2 VLAN entry
    new_l2vlan = {
        "id": int(entry.id),
        "vni_override": int(entry.vni_override),
        "name": entry.name,
        "tags": entry.tags.split(",")  # Convert comma-separated string to list
    }
    
    # Add the new entry to the first tenant's l2vlans
    for tenant in tenants_data['tenants']:
        if tenant['name'] == 'Tenant_A':
            tenant['l2vlans'].append(new_l2vlan)
            break
    
    # Write updated YAML file
    with open("TENANTS.yaml", 'w') as f:
        yaml.dump(tenants_data, f, default_flow_style=False)
    
    return Main(
        H1("YAML File Updated"),
        P(f"Entry for {entry.name} has been added to TENANTS.yaml")
    )

serve()

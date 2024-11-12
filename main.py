import pprint
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

@dataclass
class SVIEntry:
    id: str
    name: str
    ip_address_virtual: str
    tags: str
    enabled: bool = True

@app.get("/yaml-form")
def yaml_form():
    return Main(
        H1("VNI Entry Form"),
        Form(
            Div(
                Input(type="text", name="id", placeholder="ID", required=True),
                Input(
                    type="text",
                    name="vni_override",
                    placeholder="VNI Override",
                    required=True,
                ),
                Input(type="text", name="name", placeholder="Name", required=True),
                Input(
                    type="text",
                    name="tags",
                    placeholder="Tags (comma-separated)",
                    required=True,
                ),
            ),
            Button("Submit", type="submit"),
            action="/save-yaml",
            method="post",
        ),
        H1("SVI Entry Form"),
        Form(
            Div(
                Input(type="text", name="id", placeholder="SVI ID", required=True),
                Input(type="text", name="name", placeholder="SVI Name", required=True),
                Input(type="text", name="ip_address_virtual", placeholder="IP Address Virtual", required=True),
                Input(type="text", name="tags", placeholder="Tags (comma-separated)", required=True),
                Input(type="checkbox", name="enabled", checked=True, value="true"),
                Label("Enabled", for_="enabled"),
            ),
            Button("Submit", type="submit"),
            action="/save-svi-yaml",
            method="post",
        ),
    )


@app.post("/save-yaml")
def save_yaml(entry: VNIEntry):
    # Read the existing YAML file
    with open("TENANTS.yaml", "r") as f:
        tenants_data = yaml.safe_load(f)

    # Prepare the new L2 VLAN entry
    new_l2vlan = {
        "id": int(entry.id),
        "vni_override": int(entry.vni_override),
        "name": entry.name,
        "tags": entry.tags.split(","),  # Convert comma-separated string to list
    }

    # Add the new entry to the first tenant's l2vlans
    for tenant in tenants_data["tenants"]:
        if tenant["name"] == "Tenant_A":
            tenant["l2vlans"].append(new_l2vlan)
            break

    # Write updated YAML file
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(tenants_data)
    print(yaml.dump(tenants_data))
    with open("TENANTS.yaml", "w") as f:
        yaml.dump(tenants_data, f, default_flow_style=False)

    return Main(
        H1("YAML File Updated"),
        P(f"Entry for {entry.name} has been added to TENANTS.yaml"),
    )

@app.post("/save-svi-yaml")
def save_svi_yaml(entry: SVIEntry):
    # Read the existing YAML file
    with open("TENANTS.yaml", "r") as f:
        tenants_data = yaml.safe_load(f)

    # Prepare the new SVI entry
    new_svi = {
        "id": int(entry.id),
        "name": entry.name,
        "ip_address_virtual": entry.ip_address_virtual,
        "tags": entry.tags.split(","),  # Convert comma-separated string to list
        "enabled": entry.enabled
    }

    # Add the new entry to the first tenant's vrfs
    for tenant in tenants_data["tenants"]:
        if tenant["name"] == "Tenant_A":
            for vrf in tenant.get("vrfs", []):
                if vrf["name"] == "Tenant_A_OP_Zone":
                    vrf.setdefault("svis", []).append(new_svi)
                    break

    # Write updated YAML file
    with open("TENANTS.yaml", "w") as f:
        yaml.dump(tenants_data, f, default_flow_style=False)

    return Main(
        H1("YAML File Updated"),
        P(f"SVI entry for {entry.name} has been added to TENANTS.yaml"),
    )

serve()

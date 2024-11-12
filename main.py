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
    Label,
    Select,
    Option,
    Table,
    Tr,
    Th,
    Td,
    Script,
)
import yaml
import os
from dataclasses import dataclass


app = FastHTML(hdrs=(
    Script(src="https://cdn.tailwindcss.com"),
))
rt = app.route

messages = ["This is a message, which will get rendered as a paragraph"]


@app.get("/")
def home():
    page = Main(
        H1("text-2xl font-bold mb-4 text-gray-800", "Messages"),
        *[P("text-gray-600", msg) for msg in messages],
        A("text-blue-500 hover:underline", "Link to Page 2 (to add messages)", href="/page2"),
    )
    return page


@dataclass
class SVIEntry:
    id: str
    name: str
    ip_address_virtual: str
    tags: str = ""
    enabled: bool = True


@app.get("/yaml-form")
def yaml_form():
    # Read the existing YAML file to get VRF names
    with open("TENANTS.yaml", "r") as f:
        tenants_data = yaml.safe_load(f)

    # Extract VRF names from the first tenant
    vrf_names = [
        vrf["name"]
        for tenant in tenants_data.get("tenants", [])
        for vrf in tenant.get("vrfs", [])
    ]

    add = (
        H1("text-2xl font-bold mb-6 text-gray-800", "SVI Entry Form"),
        Form(
            "space-y-4 bg-white p-6 rounded-lg shadow-md",
            Div(
                "grid grid-cols-1 gap-4",
                Input(
                    "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    type="text", 
                    name="id", 
                    placeholder="SVI ID", 
                    required=True
                ),
                Input(
                    "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    type="text", 
                    name="name", 
                    placeholder="SVI Name", 
                    required=True
                ),
                Input(
                    "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    type="text",
                    name="ip_address_virtual",
                    placeholder="IP Address Virtual",
                    required=True,
                ),
                Label(
                    "block text-sm font-medium text-gray-700 mb-2",
                    "Select VRF:",
                    Div(
                        "mt-1",
                        Select(
                            "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                            *[Option(vrf, value=vrf) for vrf in vrf_names],
                            name="vrf_name",
                            required=True,
                        )
                    ),
                ),
            ),
            Button(
                "w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50",
                "Submit", 
                type="submit"
            ),
            action="/save-svi-yaml",
            method="post",
        ),
    )

    show = (
        H1("text-2xl font-bold mb-6 text-gray-800", "Currently configured SVIs"),
        Table(
            "w-full border-collapse border border-gray-300",
            Tr(
                "bg-gray-100",
                Th("border border-gray-300 px-4 py-2", "ID"),
                Th("border border-gray-300 px-4 py-2", "Name"),
                Th("border border-gray-300 px-4 py-2", "IP Address Virtual"),
                Th("border border-gray-300 px-4 py-2", "VRF Name"),
            ),
            Tr(
                "hover:bg-gray-50",
                Td("border border-gray-300 px-4 py-2", "id"),
                Td("border border-gray-300 px-4 py-2", "name"),
                Td("border border-gray-300 px-4 py-2", "ip_address_virtual"),
                Td("border border-gray-300 px-4 py-2", "vrf_name"),
            )
        ),
    )
    return Main(
        "container mx-auto px-4 py-8",
        add,
        show,
    )


@dataclass
class SVIEntry:
    id: str
    name: str
    ip_address_virtual: str
    vrf_name: str
    tags: str = ""
    enabled: bool = True


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
        # "tags": entry.tags.split(","),  # Convert comma-separated string to list
        "enabled": True,
    }

    # Add the new entry to the specified VRF
    for tenant in tenants_data["tenants"]:
        for vrf in tenant.get("vrfs", []):
            if vrf["name"] == entry.vrf_name:
                vrf.setdefault("svis", []).append(new_svi)
                break

    # Write updated YAML file
    with open("TENANTS.yaml", "w") as f:
        yaml.dump(tenants_data, f, default_flow_style=False)

    return Main(
        "container mx-auto px-4 py-8",
        H1("text-2xl font-bold mb-4 text-green-700", "YAML File Updated"),
        P("text-gray-600", f"SVI entry for {entry.name} has been added to {entry.vrf_name}"),
    )


serve()

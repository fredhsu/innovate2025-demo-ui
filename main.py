import pprint

# from shad4fast import *
# from lucide_fasthtml import Lucide
from fasthtml.common import (
    FastHTML,
    serve,
    Card,
    P,
    Title,
    Body,
    Button,
    Input,
    Div,
    H1,
    Img,
    Form,
    Main,
    Label,
    Select,
    Link,
    Section,
    Script,
)
import yaml
import os
from dataclasses import dataclass


# app = FastHTML(pico=False, hdrs=(ShadHead(theme_handle=True, tw_cdn=True),))
# app = FastHTML(pico=True)
# app = FastHTML(pico=False, hdrs=(ShadHead(tw_cdn=True),))
app = FastHTML(
    hdrs=(
        Link(
            rel="stylesheet",
            href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css",
        ),
        Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.css",
        ),
    ),
    pico=False,
)
rt = app.route


@app.get("/")
def home():
    page = Main()
    return page


@dataclass
class SVIEntry:
    id: str
    name: str
    ip_address_virtual: str
    tags: str = ""
    enabled: bool = True


def svd_id_input(id=None, **kwargs):
    return Div(
        Label("SVI ID:", htmlFor=id),
        Input(
            name="svi_id",
            placeholder="SVI ID",
            required=True,
            id=id,
        ),
        # cls="space-y-1",
        id="svi_id_block",
        **kwargs,
    )


def svd_name_input(id=None, **kwargs):
    return Div(
        Label("SVI Name:", htmlFor=id),
        Input(
            name="svi_name",
            placeholder="name",
            required=True,
            id=id,
        ),
        # cls="space-y-1",
        id="svi_name_block",
        **kwargs,
    )


def ip_address_virtual_input(id=None, **kwargs):
    return Div(
        Label("IP Address Virtual:", htmlFor=id),
        Input(
            name="ip_address_virtual",
            placeholder="1.1.1.1/24",
            required=True,
            id=id,
        ),
        # cls="space-y-1",
        id="ip_address_virtual_block",
        **kwargs,
    )


def vrf_input(vrf_names, **kw):
    vrfs = [vrf for vrf in vrf_names]
    print(vrf_names)

    # TODO: use go back to using a starred list comprehension
    return Div(
        Label(
            "Select VRF",
            Select(
                label="VRF",
                placeholder="VRF",
                name="vrf_name",
                items=["low, medium, high"],
                id="vrf-select",
                # cls="mt-1,",
                default_value=vrfs[0],
            ),
        ),
        id="vrf-input-block",
        **kw,
    )


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

    add = Card(
        Form(
            svd_id_input(id="new-svi-id"),
            ip_address_virtual_input(id="new-ip-address-virtual"),
            svd_name_input(id="new-svi-name"),
            vrf_input(vrf_names=vrf_names),
            Button(
                "Add",
                type="submit",
                # cls="w-full !mt-6",
                # TODO: use hx_post instead
            ),
            # cls="px-4 space-y-3",
            action="/save-svi-yaml",
            method="post",
        ),
        # cls="w-full",
        # title="title",
    )
    # cls="space-y-4 bg-white p-6 rounded-lg shadow-md",
    svis = tenants_data.get("tenants")[0].get("vrfs")[0].get("svis")

    content = Div(
        *[
            Card(
                P(svi.get("id")),
                title=(svi.get("name")),
            )
            for svi in svis
        ],
        id="svi-list",
        # cls="grid sm:grid-cols-2 auto-rows-fr gap-3 w-full",
    )
    show = Div(
        H1(
            "SVI List",
            # cls="text-4xl tracking-tighter font-semibold mt-10 text-center",
        ),
        content,
        # cls="container max-w-4xl flex flex-col gap-4 items-center",
    )
    return Title("Innovate 2025 Demo"), Body(
        H1(
            "Innovate 2025 Demo",
            # cls="text-4xl tracking-tighter font-semibold mt-10 text-center",
        ),
        Section(
            add,
            show,
        ),
        Script(src="https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.js"),
        # cls="flex flex-col min-h-screen items-center gap-10 p-4",
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
        Body(
            H1("text-2xl font-bold mb-4 text-green-700", "YAML File Updated"),
            P(
                "text-gray-600",
                f"SVI entry for {entry.name} has been added to {entry.vrf_name}",
            ),
            Script(
                src="https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.js"
            ),
        ),
        cls="container mx-auto px-4 py-8",
    )


serve()

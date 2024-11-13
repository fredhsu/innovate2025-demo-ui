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
    H5,
    Span,
    Form,
    Main,
    Label,
    Select,
    Option,
    Link,
    Section,
    Script,
)
import yaml
from dataclasses import dataclass


# app = FastHTML(pico=False, hdrs=(ShadHead(theme_handle=True, tw_cdn=True),))
# app = FastHTML(pico=True)
# app = FastHTML(pico=False, hdrs=(ShadHead(tw_cdn=True),))
app = FastHTML(
    hdrs=(
        # Link(href="css/output.css", rel="stylesheet"),
        # Link(
        #     rel="stylesheet",
        #     href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css",
        # ),
        # Script(src="https://cdn.tailwindcss.com"),
        Script(
            src="https://cdn.tailwindcss.com?plugins=forms,typography,aspect-ratio,line-clamp,container-queries"
        ),
        # Link(
        #     rel="stylesheet",
        #     href="https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.css",
        # ),
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
    vrf_name: str = ""
    enabled: bool = True


def svd_id_input(id=None, **kwargs):
    return Div(
        Label(
            "SVI ID:",
            htmlFor=id,
            cls="block mb-2 text-sm font-medium text-gray-900",
        ),
        Input(
            name="id",
            placeholder="SVI ID",
            required=True,
            id=id,
            cls="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        ),
        # cls="space-y-1",
        id="svi_id_block",
        **kwargs,
    )


def svd_name_input(id=None, **kwargs):
    return Div(
        Label(
            "SVI Name:",
            htmlFor=id,
            cls="block mb-2 text-sm font-medium text-gray-900",
        ),
        Input(
            name="name",
            placeholder="name",
            required=True,
            id=id,
            cls="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        ),
        # cls="space-y-1",
        id="svi_name_block",
        **kwargs,
    )


def ip_address_virtual_input(id=None, **kwargs):
    return Div(
        Label(
            "IP Address Virtual:",
            htmlFor=id,
            cls="block mb-2 text-sm font-medium text-gray-900",
        ),
        Input(
            name="ip_address_virtual",
            placeholder="1.1.1.1/24",
            required=True,
            id=id,
            cls="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        ),
        # cls="space-y-1",
        id="ip_address_virtual_block",
        **kwargs,
    )


def vrf_input(vrf_names, **kw):
    return Div(
        Label(
            "Select VRF",
            Select(
                *[Option(vrf) for vrf in vrf_names],
                label="VRF",
                placeholder="VRF",
                name="vrf_name",
                id="vrf-select",
                default_value=vrf_names[0],
                cls="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
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
                cls="my-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800",
                # TODO: use hx_post instead
            ),
            # cls="px-4 space-y-3",
            action="/save-svi-yaml",
            method="post",
            cls="max-w-sm mx-auto",
        ),
        cls=("space-y-4 bg-white p-6 rounded-lg shadow",),
    )
    svis = tenants_data.get("tenants")[0].get("vrfs")[0].get("svis")

    content = Div(
        *[
            Card(
                Div(Span("VLAN ID: ", cls="font-bold"), Span(str(svi.get("id")))),
                Div(Span("Name: ", cls="font-bold"), Span(str(svi.get("name")))),
                Div(
                    Span("IP: ", cls="font-bold"),
                    Span(str(svi.get("ip_address_virtual"))),
                ),
                cls="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 text-gray-700",
            )
            for svi in svis
        ],
        id="svi-list",
        cls="grid sm:grid-cols-2 auto-rows-fr gap-3 w-full",
    )
    show = Div(
        H1(
            "SVI List",
            cls="text-4xl tracking-tighter font-semibold mt-10 text-center",
        ),
        content,
        cls="container max-w-4xl flex flex-col gap-4 items-center",
    )
    return Title("Innovate 2025 Demo"), Body(
        H1(
            "Innovate 2025 Demo",
            cls="text-4xl tracking-tighter font-semibold mt-10 text-center",
        ),
        Section(
            add,
            show,
            # cls= "max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow",
        ),
        Script(src="https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.js"),
        cls="flex flex-col min-h-screen items-center gap-10 p-4",
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
                print("adding to {entry.vrf_name}")
                vrf.setdefault("svis", []).append(new_svi)
                break

    print(yaml.dump(tenants_data))
    # Write updated YAML file
    with open("TENANTS.yaml", "w") as f:
        yaml.dump(tenants_data, f, default_flow_style=False)

    return Main(
        Body(
            H1("text-2xl font-bold mb-4 text-green-700", "YAML File Updated"),
            P(
                "text-gray-600",
                f"SVI entry for {entry.name} has been added to {entry.name}",
            ),
        ),
        cls="container mx-auto px-4 py-8",
    )


serve()

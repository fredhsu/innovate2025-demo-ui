from fasthtml.common import (
    NotStr,
    to_xml,
    FastHTML,
    serve,
    Card,
    FileResponse,
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


app = FastHTML(
    hdrs=(
        Link(href="/css/output.css", rel="stylesheet"),
        # Link(
        #     rel="stylesheet",
        #     href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css",
        # ),
        # Script(src="https://cdn.tailwindcss.com"),
        # Script(
        #     src="https://cdn.tailwindcss.com?plugins=forms,typography,aspect-ratio,line-clamp,container-queries"
        # ),
        Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.css",
        ),
        # Script(
        #     """
        # import {
        #     Card,
        #     CardContent,
        #     CardDescription,
        #     CardFooter,
        #     CardHeader,
        #     CardTitle,
        # } from "@/components/ui/card"
        # """,
        #     type="module",
        # ),
    ),
    pico=False,
)
rt = app.route


@app.get("/css/output.css")
def css():
    return FileResponse("output.css")


@app.get("/")
def home():
    page = Main()
    return page


@dataclass
class SVIEntry:
    id: str
    name: str
    ip_address_virtual: str
    ticket_id: str
    tags: str = ""
    vrf_name: str = ""
    enabled: bool = True


def svd_id_input(id=None, **kwargs):
    return Div(
        Label(
            "SVI ID:",
            htmlFor=id,
            cls="block mb-2 font-medium text-gray-900",
        ),
        Input(
            name="id",
            placeholder="SVI ID",
            required=True,
            id=id,
            cls="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
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
            cls="block mb-2 font-medium text-gray-900",
        ),
        Input(
            name="name",
            placeholder="name",
            required=True,
            id=id,
            cls="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        ),
        # cls="space-y-1",
        id="svi_name_block",
        **kwargs,
    )


def ticket_id_input(id=None, **kwargs):
    return Div(
        Label(
            "Ticket ID:",
            htmlFor=id,
            cls="block mb-2 font-medium text-gray-900",
        ),
        Input(
            name="ticket_id",
            placeholder="Ticket ID",
            required=True,
            id=id,
            cls="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        ),
        id="ticket_id_block",
        **kwargs,
    )


def ip_address_virtual_input(id=None, **kwargs):
    return Div(
        Label(
            "IP Address Virtual:",
            htmlFor=id,
            cls="block mb-2 font-medium text-gray-900",
        ),
        Input(
            name="ip_address_virtual",
            placeholder="1.1.1.1/24",
            required=True,
            id=id,
            cls="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
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
                cls="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
            ),
        ),
        id="vrf-input-block",
        **kw,
    )

def svi_card(svi, vrf_name=None):
    """
    Generate a card for an SVI entry
    
    :param svi: Dictionary containing SVI details
    :param vrf_name: Optional VRF name, defaults to 'VRF-A' if not provided
    :return: Card component for the SVI
    """
    vrf_name = vrf_name or svi.get('vrf_name', 'VRF-A')
    return Card(
        Div(H5(svi.get("name"), cls="text-xl font-bold text-gray-900")),
        Div(Span("VLAN ID: ", cls="font-bold"), Span(str(svi.get("id")))),
        Div(
            Span("IP: ", cls="font-bold"),
            Span(str(svi.get("ip_address_virtual"))),
        ),
        Div(
            Span("VRF: ", cls="font-bold"),
            Span(str(vrf_name)),
        ),
        Button(
            "Delete",
            hx_delete=f"/delete-svi/{svi.get('id')}/{vrf_name}",
            hx_target="closest .card",
            hx_swap="outerHTML",
            cls="mt-2 text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg px-5 py-2.5 me-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 focus:outline-none dark:focus:ring-red-800",
        ),
        cls="card text-lg flex flex-col h-full w-80 p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 text-gray-700",
    )


@app.get("/test")
def test():
    return Title("Test"), Body(
        H1("Test"),
        NotStr("""

    <Card>
    <CardHeader>
        <CardTitle>Card Title</CardTitle>
        <CardDescription>Card Description</CardDescription>
    </CardHeader>
    <CardContent>
        <p>Card Content</p>
    </CardContent>
    <CardFooter>
        <p>Card Footer</p>
    </CardFooter>
    </Card>
    """),
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
            ticket_id_input(id="new-ticket-id"),
            vrf_input(vrf_names=vrf_names),
            Button(
                "Add",
                type="submit",
                hx_post="/save-svi-yaml",
                hx_target="#svi-list",
                hx_swap="beforeend",
                cls="my-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800",
            ),
            cls="max-w-sm mx-auto",
        ),
        cls=("text-lg space-y-4 bg-white p-6 rounded-lg shadow",),
    )
    # Extract all unique VRF names
    vrf_names = [
        vrf["name"]
        for tenant in tenants_data.get("tenants", [])
        for vrf in tenant.get("vrfs", [])
    ]

    # Get SVIs from the first VRF initially
    first_vrf = tenants_data.get("tenants")[0].get("vrfs")[0]
    svis = first_vrf.get("svis")
    vrf_name = first_vrf.get("name", "VRF-A")
    for svi in svis:
        svi["vrf_name"] = vrf_name

    content = Div(
        *[svi_card(svi) for svi in svis],
        id="svi-list",
        cls="grid grid-cols-2 gap-6 w-full justify-center max-w-4xl mx-auto",
    )
    # Add VRF filter dropdown
    vrf_filter = Div(
        Label(
            "Filter by VRF:",
            Select(
                *[Option(vrf, value=vrf) for vrf in vrf_names],
                name="vrf_filter",
                id="vrf-filter-select",
                hx_get="/filter-svis",
                hx_target="#svi-list",
                hx_swap="outerHTML",
                cls="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
            ),
            cls="block mb-2 text-xl font-medium text-gray-900",
        ),
        cls="mb-4",
    )

    show = Div(
        H1(
            "SVI List",
            cls="text-5xl font-extrabold dark:text-white",
        ),
        vrf_filter,
        content,
        cls="container max-w-4xl flex flex-col gap-4 items-center",
    )
    return Title("Arista Innovate 2024 AVD Demo"), Body(
        H1(
            "Arista Innovate 2024 AVD Demo",
            cls="mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white",
        ),
        Section(
            add,
            show,
        ),
        Script(src="https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.js"),
        cls="flex flex-col min-h-screen items-center gap-10 p-4",
    )


@app.post("/save-svi-yaml")
def save_svi_yaml(entry: SVIEntry):
    # Read the existing YAML file
    with open("TENANTS.yaml", "r") as f:
        tenants_data = yaml.safe_load(f)

    # Print the ticket ID (but do not save it)
    print(f"Ticket ID for this SVI: {entry.ticket_id}")

    # Prepare the new SVI entry
    new_svi = {
        "id": int(entry.id),
        "name": entry.name,
        "ip_address_virtual": entry.ip_address_virtual,
        "enabled": True,
    }

    # Add the new entry to the specified VRF
    for tenant in tenants_data["tenants"]:
        for vrf in tenant.get("vrfs", []):
            if vrf["name"] == entry.vrf_name:
                print(f"adding to {entry.vrf_name}")
                vrf.setdefault("svis", []).append(new_svi)
                break

    # Write updated YAML file
    with open("TENANTS.yaml", "w") as f:
        yaml.dump(tenants_data, f, default_flow_style=False)

    # Return an HTML fragment for HTMX to insert
    return svi_card({
        "name": new_svi.get("name"),
        "id": entry.id,
        "ip_address_virtual": entry.ip_address_virtual
    }, entry.vrf_name)


@app.delete("/delete-svi/{id}/{vrf_name}")
def delete_svi(id: int, vrf_name: str):
    # Read the existing YAML file
    with open("TENANTS.yaml", "r") as f:
        tenants_data = yaml.safe_load(f)

    # Remove the SVI entry from the specified VRF
    for tenant in tenants_data["tenants"]:
        for vrf in tenant.get("vrfs", []):
            if vrf["name"] == vrf_name:
                # Remove the SVI with the matching ID
                vrf["svis"] = [svi for svi in vrf.get("svis", []) if svi["id"] != id]
                break

    # Write updated YAML file
    with open("TENANTS.yaml", "w") as f:
        yaml.dump(tenants_data, f, default_flow_style=False)

    # Return an empty response to indicate successful deletion
    return ""


@app.get("/filter-svis")
def filter_svis(vrf_filter: str = "VRF-A"):
    # Read the existing YAML file
    with open("TENANTS.yaml", "r") as f:
        tenants_data = yaml.safe_load(f)

    # Find SVIs for the selected VRF
    filtered_svis = []
    for tenant in tenants_data.get("tenants", []):
        for vrf in tenant.get("vrfs", []):
            if vrf["name"] == vrf_filter:
                filtered_svis = vrf.get("svis", [])
                break

    # Add VRF name to each SVI
    for svi in filtered_svis:
        svi["vrf_name"] = vrf_filter

    # Return HTML fragment with filtered SVIs
    return Div(
        *[svi_card(svi) for svi in filtered_svis],
        id="svi-list",
        cls="grid text-lg grid-cols-2 gap-6 w-full justify-center max-w-4xl mx-auto",
    )


app.static_route("/css", static_path="./css")
app.static_route("/images", static_path="./images")
serve()

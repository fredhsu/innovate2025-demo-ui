-- Create table for tenants
CREATE TABLE tenants (
    tenant_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    mac_vrf_vni_base INTEGER NOT NULL
);

-- Create table for VRFs (Virtual Routing and Forwarding)
CREATE TABLE vrfs (
    vrf_id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    vrf_vni INTEGER NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    UNIQUE (tenant_id, name)
);

-- Create table for VTEP diagnostics
CREATE TABLE vtep_diagnostics (
    vtep_id SERIAL PRIMARY KEY,
    vrf_id INTEGER NOT NULL UNIQUE,
    loopback INTEGER NOT NULL,
    loopback_ip_range CIDR NOT NULL,
    FOREIGN KEY (vrf_id) REFERENCES vrfs(vrf_id)
);

-- Create table for SVIs (Switch Virtual Interfaces)
CREATE TABLE svis (
    svi_id SERIAL PRIMARY KEY,
    vrf_id INTEGER NOT NULL,
    vlan_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    ip_address_virtual CIDR,
    FOREIGN KEY (vrf_id) REFERENCES vrfs(vrf_id),
    UNIQUE (vrf_id, vlan_id)
);

-- Create table for SVI tags
CREATE TABLE svi_tags (
    svi_tag_id SERIAL PRIMARY KEY,
    svi_id INTEGER NOT NULL,
    tag VARCHAR(50) NOT NULL,
    FOREIGN KEY (svi_id) REFERENCES svis(svi_id),
    UNIQUE (svi_id, tag)
);

-- Insert sample data based on the YAML example
INSERT INTO tenants (name, mac_vrf_vni_base) 
VALUES ('Tenant_A', 10000);

INSERT INTO vrfs (tenant_id, name, vrf_vni)
VALUES (
    (SELECT tenant_id FROM tenants WHERE name = 'Tenant_A'),
    'Tenant_A_OP_Zone',
    10
);

INSERT INTO vtep_diagnostics (vrf_id, loopback, loopback_ip_range)
VALUES (
    (SELECT vrf_id FROM vrfs WHERE name = 'Tenant_A_OP_Zone'),
    100,
    '10.255.1.0/24'
);

INSERT INTO svis (vrf_id, vlan_id, name, enabled, ip_address_virtual)
VALUES (
    (SELECT vrf_id FROM vrfs WHERE name = 'Tenant_A_OP_Zone'),
    110,
    'Tenant_A_OP_Zone_1',
    true,
    '10.1.10.1/24'
);

INSERT INTO svi_tags (svi_id, tag)
VALUES (
    (SELECT svi_id FROM svis WHERE name = 'Tenant_A_OP_Zone_1'),
    'opzone'
);

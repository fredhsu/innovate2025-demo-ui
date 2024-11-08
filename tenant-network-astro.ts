// src/pages/index.astro
---
import Layout from '../layouts/Layout.astro';
import TenantDashboard from '../components/TenantDashboard';
---

<Layout title="Tenant Network Manager">
  <main class="container mx-auto p-4">
    <TenantDashboard client:load />
  </main>
</Layout>

// src/layouts/Layout.astro
---
interface Props {
  title: string;
}

const { title } = Astro.props;
---

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="description" content="Tenant Network Management System" />
    <meta name="viewport" content="width=device-width" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>{title}</title>
  </head>
  <body class="min-h-screen bg-gray-50">
    <slot />
  </body>
</html>

<style is:global>
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
</style>

// src/components/TenantDashboard.tsx
import { useState, useEffect } from 'react';
import NewSviForm from './NewSviForm';
import TenantTable from './TenantTable';
import { Network, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import type { Tenant, Vrf, Svi } from '../types';

export default function TenantDashboard() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [vrfs, setVrfs] = useState<Vrf[]>([]);
  const [svis, setSvis] = useState<Svi[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewSviForm, setShowNewSviForm] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [tenantsRes, vrfsRes, svisRes] = await Promise.all([
        fetch('http://localhost:3000/tenants'),
        fetch('http://localhost:3000/vrfs'),
        fetch('http://localhost:3000/svis')
      ]);

      const [tenantsData, vrfsData, svisData] = await Promise.all([
        tenantsRes.json(),
        vrfsRes.json(),
        svisRes.json()
      ]);

      setTenants(tenantsData);
      setVrfs(vrfsData);
      setSvis(svisData);
    } catch (err) {
      setError('Failed to fetch network data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Network className="w-6 h-6" />
          Tenant Network Manager
        </h1>
        <Button onClick={() => setShowNewSviForm(true)}>New SVI</Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <NewSviForm 
        show={showNewSviForm}
        onClose={() => setShowNewSviForm(false)}
        vrfs={vrfs}
        onSuccess={() => {
          fetchData();
          setShowNewSviForm(false);
        }}
      />

      {tenants.map(tenant => (
        <TenantTable
          key={tenant.tenant_id}
          tenant={tenant}
          vrfs={vrfs.filter(vrf => vrf.tenant_id === tenant.tenant_id)}
          svis={svis}
        />
      ))}
    </div>
  );
}

// src/components/NewSviForm.tsx
import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Vrf } from '../types';

interface NewSviFormProps {
  show: boolean;
  onClose: () => void;
  vrfs: Vrf[];
  onSuccess: () => void;
}

export default function NewSviForm({ show, onClose, vrfs, onSuccess }: NewSviFormProps) {
  const [formData, setFormData] = useState({
    vrf_id: '',
    vlan_id: '',
    name: '',
    ip_address_virtual: '',
    tags: '',
    enabled: true
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const response = await fetch('http://localhost:3000/svis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          vrf_id: parseInt(formData.vrf_id),
          vlan_id: parseInt(formData.vlan_id),
          tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean)
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create SVI');
      }

      onSuccess();
      setFormData({
        vrf_id: '',
        vlan_id: '',
        name: '',
        ip_address_virtual: '',
        tags: '',
        enabled: true
      });
    } catch (err) {
      setError('Failed to create SVI');
    }
  };

  return (
    <Dialog open={show} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New SVI</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            value={formData.vrf_id}
            onValueChange={(value) => setFormData({ ...formData, vrf_id: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select VRF" />
            </SelectTrigger>
            <SelectContent>
              {vrfs.map(vrf => (
                <SelectItem key={vrf.vrf_id} value={vrf.vrf_id.toString()}>
                  {vrf.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Input
            placeholder="VLAN ID"
            type="number"
            value={formData.vlan_id}
            onChange={(e) => setFormData({ ...formData, vlan_id: e.target.value })}
          />

          <Input
            placeholder="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />

          <Input
            placeholder="IP Address Virtual (CIDR)"
            value={formData.ip_address_virtual}
            onChange={(e) => setFormData({ ...formData, ip_address_virtual: e.target.value })}
          />

          <Input
            placeholder="Tags (comma-separated)"
            value={formData.tags}
            onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
          />

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">Create SVI</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// src/components/TenantTable.tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Tenant, Vrf, Svi } from '../types';

interface TenantTableProps {
  tenant: Tenant;
  vrfs: Vrf[];
  svis: Svi[];
}

export default function TenantTable({ tenant, vrfs, svis }: TenantTableProps) {
  return (
    <div className="rounded-lg border bg-white p-6">
      <h2 className="text-xl font-semibold mb-4">
        Tenant: {tenant.name}
      </h2>
      
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>VRF</TableHead>
            <TableHead>VNI</TableHead>
            <TableHead>VLAN ID</TableHead>
            <TableHead>SVI Name</TableHead>
            <TableHead>IP Address</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Tags</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {vrfs.map(vrf => (
            svis
              .filter(svi => svi.vrf_id === vrf.vrf_id)
              .map(svi => (
                <TableRow key={svi.svi_id}>
                  <TableCell>{vrf.name}</TableCell>
                  <TableCell>{vrf.vrf_vni}</TableCell>
                  <TableCell>{svi.vlan_id}</TableCell>
                  <TableCell>{svi.name}</TableCell>
                  <TableCell>{svi.ip_address_virtual}</TableCell>
                  <TableCell>
                    <span 
                      className={`px-2 py-1 rounded-full text-xs ${
                        svi.enabled 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {svi.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1 flex-wrap">
                      {svi.tags.map(tag => (
                        <span 
                          key={tag} 
                          className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </TableCell>
                </TableRow>
              ))
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

// src/types.ts
export interface Tenant {
  tenant_id: number;
  name: string;
  mac_vrf_vni_base: number;
}

export interface Vrf {
  vrf_id: number;
  tenant_id: number;
  name: string;
  vrf_vni: number;
}

export interface Svi {
  svi_id: number;
  vrf_id: number;
  vlan_id: number;
  name: string;
  enabled: boolean;
  ip_address_virtual: string;
  tags: string[];
}

// astro.config.mjs
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [react(), tailwind()],
});

// package.json
{
  "name": "tenant-network-manager",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "@astrojs/react": "^3.0.0",
    "@astrojs/tailwind": "^5.0.0",
    "@radix-ui/react-dialog": "^1.0.4",
    "@radix-ui/react-select": "^1.2.2",
    "astro": "^3.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "lucide-react": "^0.263.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwind-merge": "^1.14.0",
    "tailwindcss": "^3.3.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.21",
    "@types/react-dom": "^18.2.7",
    "typescript": "^5.2.2"
  }
}

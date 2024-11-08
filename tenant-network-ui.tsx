import { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Network, Plus, RefreshCw } from "lucide-react";

const TenantNetworkDashboard = () => {
  const [tenants, setTenants] = useState([]);
  const [vrfs, setVrfs] = useState([]);
  const [svis, setSvis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedVrf, setSelectedVrf] = useState("");
  const [newSvi, setNewSvi] = useState({
    vrf_id: "",
    vlan_id: "",
    name: "",
    enabled: true,
    ip_address_virtual: "",
    tags: []
  });
  const [showNewSviDialog, setShowNewSviDialog] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch tenants
      const tenantsResponse = await fetch('http://localhost:3000/tenants');
      const tenantsData = await tenantsResponse.json();
      setTenants(tenantsData);

      // Fetch VRFs for all tenants
      const vrfsPromises = tenantsData.map(tenant =>
        fetch(`http://localhost:3000/vrfs?tenant_id=${tenant.tenant_id}`)
          .then(res => res.json())
      );
      const vrfsData = await Promise.all(vrfsPromises);
      setVrfs(vrfsData.flat());

      // Fetch SVIs for all VRFs
      const svisPromises = vrfsData.flat().map(vrf =>
        fetch(`http://localhost:3000/svis?vrf_id=${vrf.vrf_id}`)
          .then(res => res.json())
      );
      const svisData = await Promise.all(svisPromises);
      setSvis(svisData.flat());
    } catch (err) {
      setError("Failed to fetch network data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateSvi = async (e) => {
    e.preventDefault();
    setError(null);
    
    try {
      const response = await fetch('http://localhost:3000/svis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newSvi,
          vrf_id: parseInt(selectedVrf),
          vlan_id: parseInt(newSvi.vlan_id),
          tags: newSvi.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create SVI');
      }

      await fetchData();
      setShowNewSviDialog(false);
      setNewSvi({
        vrf_id: "",
        vlan_id: "",
        name: "",
        enabled: true,
        ip_address_virtual: "",
        tags: []
      });
    } catch (err) {
      setError("Failed to create new SVI. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Network className="w-6 h-6" />
          Tenant Network Dashboard
        </h1>
        <Dialog open={showNewSviDialog} onOpenChange={setShowNewSviDialog}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="w-4 h-4" />
              New SVI
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New SVI</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateSvi} className="space-y-4">
              <Select
                value={selectedVrf}
                onValueChange={setSelectedVrf}
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
                value={newSvi.vlan_id}
                onChange={e => setNewSvi({...newSvi, vlan_id: e.target.value})}
              />
              
              <Input
                placeholder="Name"
                value={newSvi.name}
                onChange={e => setNewSvi({...newSvi, name: e.target.value})}
              />
              
              <Input
                placeholder="IP Address Virtual (CIDR)"
                value={newSvi.ip_address_virtual}
                onChange={e => setNewSvi({...newSvi, ip_address_virtual: e.target.value})}
              />
              
              <Input
                placeholder="Tags (comma-separated)"
                value={newSvi.tags}
                onChange={e => setNewSvi({...newSvi, tags: e.target.value})}
              />
              
              <DialogFooter>
                <Button type="submit">Create SVI</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {tenants.map(tenant => (
        <div key={tenant.tenant_id} className="mb-8">
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
              {vrfs
                .filter(vrf => vrf.tenant_id === tenant.tenant_id)
                .map(vrf => (
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
                          <span className={`px-2 py-1 rounded-full text-xs ${svi.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {svi.enabled ? 'Enabled' : 'Disabled'}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            {svi.tags.map(tag => (
                              <span key={tag} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
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
      ))}
    </div>
  );
};

export default TenantNetworkDashboard;

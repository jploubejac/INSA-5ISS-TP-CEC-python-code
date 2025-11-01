import openstack 

def nettoyage(conn):
    for server in conn.compute.servers():
        if server.name in ["fabricelebon_py", "solangelaclient_py", "div_py", "mule_py", "sous_py", "add_py"]:
            print(f"Suppression de la machine {server.name} ({server.id})...")
            conn.compute.delete_server(server, ignore_missing=True)
            conn.compute.wait_for_delete(server)

    for router in conn.network.routers():
        if router.name in ["router_public_1", "router_1_2"]:
            print(f"Suppression du routeur {router.name} ({router.id})...")
            try:
                conn.network.update_router(router, external_gateway_info=None)
                print("  Gateway supprimée.")
            except Exception as e:
                print(f"  Erreur lors de la suppression de la gateway : {e}")
            ports = list(conn.network.ports(device_id=router.id))
            for port in ports:
                for ip in port.fixed_ips:
                    try:
                        conn.network.remove_interface_from_router(router, subnet_id=ip['subnet_id'])
                        print(f"  Interface sur subnet {ip['subnet_id']} détachée.")
                    except Exception as e:
                        print(f"  Erreur lors du détachement de l'interface : {e}")
            try:
                conn.network.delete_router(router, ignore_missing=True)
                print(f"  Routeur supprimé.")
            except Exception as e:
                print(f"  Erreur lors de la suppression du routeur : {e}")

    for subnet in conn.network.subnets():
        if subnet.name in ["mysubnet1", "mysubnet2"]:
            print(f"Suppression du sous-réseau {subnet.name} ({subnet.id})...")
            conn.network.delete_subnet(subnet, ignore_missing=True)

    for net in conn.network.networks():
        if net.name in ["mynetwork1", "mynetwork2"]:
            print(f"Suppression du réseau {net.name} ({net.id})...")
            conn.network.delete_network(net, ignore_missing=True)

    print("Nettoyage terminé")

def réseaux(conn):
    public_network = conn.network.find_network("public")
    sub_public = None
    for subnet in conn.network.subnets(network_id=public_network.id):
        if subnet.name == "sub-public":
            sub_public = subnet
            break
    if sub_public is None: return errprint("Public subnet not found")
    network1 = conn.network.create_network(name="mynetwork1")
    print("Le réseau Network1 ID:", network1.id)
    subnet1a = conn.network.create_subnet(
        name="mysubnet1a",
        network_id=network1.id,
        ip_version='4',
        cidr='017.015.014.0/25'  
    )
    print("Le sous-réseau Subnet1a ID:", subnet1a.id)
    subnet1b = conn.network.create_subnet(
        name="mysubnet1b",
        network_id=network1.id,
        ip_version='4',
        cidr='017.015.014.128/25' 
    )
    print("Le sous-réseau Subnet1b ID:", subnet1b.id)
    network2 = conn.network.create_network(name="mynetwork2")
    print("Le réseau Network2 ID:", network2.id)
    subnet2 = conn.network.create_subnet(
        name="mysubnet2",
        network_id=network2.id,
        ip_version='4',
        cidr='016.038.014.0/24'
    )
    print("Le sous-réseau Subnet2 ID:", subnet2.id)
    router_public_1 = conn.network.create_router(name="router_public_1")
    print("Le routeur Router_Public_1 ID:", router_public_1.id)
    conn.network.add_interface_to_router(router_public_1, subnet_id=subnet1a.id)
    conn.network.update_router(router_public_1, external_gateway_info={"network_id": public_network.id})
    print("Le routeur Router_Public_1 a été connecté au sous-réseau Subnet1a avec comme passerelle (gateway) le réseau public.")

    router_1_2 = conn.network.create_router(name="router_1_2")
    print("Le routeur Router_1_2 ID:", router_1_2.id)
    conn.network.add_interface_to_router(router_1_2, subnet_id=subnet1b.id)
    conn.network.add_interface_to_router(router_1_2, subnet_id=subnet2.id)
    print("Le routeur Router_1_2 a été connecté au sous-réseau Subnet1b et au sous-réseau Subnet2.")
    print("Configuration des réseaux terminée")
    return network1, network2

def machine(conn, network1, network2):
    image = conn.compute.find_image("Ubuntu4CLV")
    flavor = conn.compute.find_flavor("small2")
    name = ["fabricelebon_py", "solangelaclient_py", "div_py", "mule_py", "sous_py","add_py"]

    for n in name:
        if n == "fabricelebon_py":
            net = network1.id
        else:
            net = network2.id
        server = conn.compute.create_server(
            name=n,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": net}]
        )
        print("La machine", n, "a été créée avec l'ID:", server.id)
    print("Toutes les machines ont été créées")

conn = openstack.connect()
nettoyage(conn)
machine(conn, *réseaux(conn))
print ("Configuration terminée. J'espère que tout fonctionne bien !")
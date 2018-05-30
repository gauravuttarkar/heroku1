"""Code which actually takes care of application API calls or other business logic"""
from yellowant.messageformat import MessageClass, MessageAttachmentsClass
from yellowant import YellowAnt
import traceback
from threading import Thread
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from msrestazure.azure_exceptions import CloudError
from haikunator import Haikunator
from yellowant_api.models import azure

class CreateVMThread(Thread):
    """Creates a VM using a separate thread."""
    def __init__(self,args,user_integration):
        ''' Constructor. '''
        Thread.__init__(self)
        self.args = args
        self.user_integration = user_integration

    def run(self):
        """Method which runs when the thread is started"""
        global GROUP_NAME, VM_NAME, USERNAME, PASSWORD

        message = MessageClass()
        credentials, subscription_id = get_credentials()
        compute_client = ComputeManagementClient(credentials, subscription_id)
        network_client = NetworkManagementClient(credentials, subscription_id)
        GROUP_NAME = self.args.get("Resource-Group")
        VM_NAME = self.args.get("VM-Name")
        NIC_NAME = self.args.get("nic_name")
        IP_CONFIG_NAME = self.args.get("ipconfig_name")
        USERNAME = self.args.get("username")
        PASSWORD = self.args.get("password")
        VNET_NAME = self.args.get("vnet_name")
        SUBNET_NAME =self.args.get("subnet_name")
        LOCATION = self.args.get("location")

        try:
            # Create a NIC
            nic = create_nic(network_client, VNET_NAME, SUBNET_NAME, IP_CONFIG_NAME, NIC_NAME)

            #############
            # VM Sample #
            #############

            # Create Linux VM
            print('\nCreating Linux Virtual Machine')
            vm_parameters = create_vm_parameters(nic.id, VM_REFERENCE['linux'], VM_NAME, USERNAME, PASSWORD,LOCATION)
            async_vm_creation = compute_client.virtual_machines.create_or_update(
                GROUP_NAME, VM_NAME, vm_parameters)
            # async_vm_creation.wait()
            message.message_text = "You are Virtual Machine is being created"

        except CloudError:
            print('A VM operation failed:', traceback.format_exc(), sep='\n')
            message.message_text = "There was an error.Please try again"

        else:
            webhook_message = MessageClass()
            webhook_message.message_text = "VM created successfully"
            attachment = MessageAttachmentsClass()
            attachment.title = VM_NAME

            webhook_message.attach(attachment)
            yellowant_user_integration_object = YellowAnt(access_token=self.user_integration.yellowant_integration_token)
            yellowant_user_integration_object.create_webhook_message(
                requester_application=self.user_integration.yellowant_integration_id,
                webhook_name="start_vm_webhook",
                **webhook_message.get_dict())
            print('All example operations completed successfully!')

haikunator = Haikunator()
LOCATION = 'westus'

# Resource Group
GROUP_NAME = 'test2'

# Network
VNET_NAME = 'azure-sample-vnet1'
SUBNET_NAME = 'azure-sample-subnet1'

# VM
OS_DISK_NAME = 'azure-sample-osdisk'
STORAGE_ACCOUNT_NAME = haikunator.haikunate(delimiter='')

IP_CONFIG_NAME = 'azure-sample-ip-config'
NIC_NAME = 'azure-sample-nic1'
USERNAME = 'userlogin'
PASSWORD = 'Pa$$w0rd91'
VM_NAME = 'VmName'

AZURE_TENANT_ID="b4797bec-4e9f-4515-90d4-398536ab71b7"
AZURE_CLIENT_ID="1431ca73-1d91-46c7-b674-55fda3f4ee04"
AZURE_CLIENT_SECRET="0KdUhM/nVaotys/fN6DACONe8iY8XlPZGCc2q3yHLxc="
AZURE_SUBSCRIPTION_ID="bb1348ac-601d-4100-8520-6099fa2ac73b"

VM_REFERENCE = {
    'linux': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '16.04.0-LTS',
        'version': 'latest'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServerEssentials',
        'offer': 'WindowsServerEssentials',
        'sku': 'WindowsServerEssentials',
        'version': 'latest'
    }
}

def get_credentials():
    subscription_id = AZURE_SUBSCRIPTION_ID
    credentials = ServicePrincipalCredentials(
        client_id=AZURE_CLIENT_ID,
        secret=AZURE_CLIENT_SECRET,
        tenant=AZURE_TENANT_ID
    )
    return credentials, subscription_id

def create_resource_group(args,user_integration):
    # global GROUP_NAME,VM_NAME
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    resource_client = ResourceManagementClient(credentials, subscription_id)
    print('\nCreating Resource Group')
    GROUP_NAME = args.get("Resource-Group")

    resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})
    print("Resource group has been created")
    message.message_text = "Your resource group is created"
    return message


def delete_resource_group(args,user_integration):
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    resource_client = ResourceManagementClient(credentials, subscription_id)
    GROUP_NAME = args.get("Resource-Group")
    print('\nDelete Resource Group')
    delete_async_operation = resource_client.resource_groups.delete(GROUP_NAME)
    #delete_async_operation.wait()
    print("Resource group has been deleted")
    message.message_text = "Your resource group has been deleted"
    return message


def create_vm(args,user_integration):
    threadObj = CreateVMThread(args,user_integration)
    # async_vm_start = compute_client.virtual_machines.start(GROUP_NAME, VM_NAME)
    # async_vm_start.wait()
    threadObj.daemon = True
    threadObj.start()
    message=MessageClass()
    message.message_text = "Creating VM"
    return message

def delete_vm(args,user_integration):
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    resource_client = ResourceManagementClient(credentials, subscription_id)
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)
    try:
        GROUP_NAME = args.get('group_name')
        VM_NAME = args.get('vm_name')
        print(GROUP_NAME,VM_NAME)
        async_vm_delete = compute_client.virtual_machines.delete(GROUP_NAME, VM_NAME)
        async_vm_delete.wait()

        print('Delete successfull')
        message.message_text = "Delete successfull"
    except:
        print('Delete unsuccessfull')
        message.message_text = "Delete unsuccessfull"

    return message

def start_vm(args , user_integration):
    GROUP_NAME=args.get('group_name')
    VM_NAME=args.get('vm_name')
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    # Start the VM
    print('\nStart VM')
    async_vm_start = compute_client.virtual_machines.start(GROUP_NAME, VM_NAME)


    message.message_text = VM_NAME + " started"

    return message

def stop_vm(args , user_integration):
    GROUP_NAME=args.get('group_name')
    VM_NAME=args.get('vm_name')
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    print('\nStop VM')
    async_vm_stop = compute_client.virtual_machines.power_off(GROUP_NAME, VM_NAME)
    message.message_text =  VM_NAME + " stopped"

    return message

def restart_vm(args , user_integration):
    GROUP_NAME=args.get('group_name')
    VM_NAME=args.get('vm_name')
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)

    print('\nRestart VM')
    async_vm_restart = compute_client.virtual_machines.restart(GROUP_NAME, VM_NAME)
    # async_vm_restart.wait()
    message.message_text = VM_NAME + " Restarted"
    return message

def list_all_vms(args , user_integration):
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    print('Integration ID is',user_integration.yellowant_integration_token)
    print('ID is ', user_integration.id)

    print('\nList VMs in subscription')
    data = {'list': []}
    message.message_text = "Listing all VMs"
    for vm in compute_client.virtual_machines.list_all():
        print("\tVM: {}".format(vm.name))
        message.message_text = message.message_text + "\n" + vm.name
        data['list'].append({"VM_name":vm.name})
    message.data = data
    return message

def list_all_vms_in_rg(args,user_integration):
    message = MessageClass()
    GROUP_NAME = args.get("Resource-Group")
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    print('\nList VMs in resource group')
    message.message_text = "Listing all VMs"
    data = {'list': []}
    for vm in compute_client.virtual_machines.list(GROUP_NAME):
        print("\tVM: {}".format(vm.name))
        data['list'].append({"VM_name": vm.name})
        print('inside for')
        message.message_text=message.message_text+"\n"+vm.name
    message.data = data
    return message

def list_regions(args,users):
    m = MessageClass()
    credentials, subscription_id = get_credentials()
    client = ResourceManagementClient(credentials, subscription_id)
    data = {'list': []}
    for item in client.resource_groups.list():
        print(item.name)
        data['list'].append({"Resource_name":item.name})
    print(data)
    m.data = data
    return m

def create_disk(args , user_integration):
    message = MessageClass()
    GROUP_NAME = args.get("Resource-Group")
    SIZE = args.get("disk_size")
    DISK_NAME = args.get("disk_name")
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)

    print('\nCreate (empty) managed Data Disk')
    async_disk_creation = compute_client.disks.create_or_update(
        GROUP_NAME,
        DISK_NAME,
        {
            'location': LOCATION,
            'disk_size_gb': SIZE,
            'creation_data': {
                'create_option': DiskCreateOption.empty
            }
        }
    )
    #async_disk_creation.wait()
    message.message_text = "Disk created"

    return message


def attach_disk(args , user_integration):
    message = MessageClass()
    GROUP_NAME = args.get("Resource-Group")
    VM_NAME = args.get("vm_name")
    DISK_NAME = args.get("disk_name")

    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)

    virtual_machine = compute_client.virtual_machines.get(
        GROUP_NAME,
        VM_NAME
    )
    print('Starting attachment')
    # Attach data disk
    data_disk=compute_client.disks.get(GROUP_NAME, DISK_NAME)
    print('\nGet Virtual Machine by Name')
    virtual_machine = compute_client.virtual_machines.get(
    GROUP_NAME,
    VM_NAME
    )
    # Attach data disk
    print('\nAttach Data Disk')
    virtual_machine.storage_profile.data_disks.append({
    'lun': 12,
    'name': data_disk.name,
    'create_option': DiskCreateOption.attach,
    'managed_disk': {
        'id': data_disk.id
    }
    })
    async_disk_attach = compute_client.virtual_machines.create_or_update(
    GROUP_NAME,
    virtual_machine.name,
    virtual_machine
    )
    #async_disk_attach.wait()
    message.message_text = "Disk attached to VM"

    return message

def detach_disk(args,user_integration):
    # Detach data disk
    message = MessageClass()
    print('\nDetach Data Disk')
    GROUP_NAME = args.get("Resource-Group")
    VM_NAME = args.get("vm_name")
    DISK_NAME = args.get("disk_name")
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)

    virtual_machine = compute_client.virtual_machines.get(
    GROUP_NAME,
    VM_NAME
    )
    data_disks = virtual_machine.storage_profile.data_disks
    data_disks[:] = [disk for disk in data_disks if disk.name != DISK_NAME]
    async_vm_update = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME,
        virtual_machine
    )
    #virtual_machine = async_vm_update.result()
    message.message_text = "Disk deattached from VM"

    return message

#=========================================================================================================================================

def create_nic(network_client,VNET_NAME,SUBNET_NAME,IP_CONFIG_NAME,NIC_NAME):
    """Create a Network Interface for a VM.
    """
    # Create VNet
    global GROUP_NAME
    print('\nCreate Vnet')
    async_vnet_creation = network_client.virtual_networks.create_or_update(
        GROUP_NAME,
        VNET_NAME,
        {
            'location': LOCATION,
            'address_space': {
                'address_prefixes': ['10.0.0.0/16']
            }
        }
    )
    async_vnet_creation.wait()

    # Create Subnet
    print('\nCreate Subnet')
    async_subnet_creation = network_client.subnets.create_or_update(
        GROUP_NAME,
        VNET_NAME,
        SUBNET_NAME,
        {'address_prefix': '10.0.0.0/24'}
    )
    subnet_info = async_subnet_creation.result()

    # Create NIC
    print('\nCreate NIC')
    async_nic_creation = network_client.network_interfaces.create_or_update(
        GROUP_NAME,
        NIC_NAME,
        {
            'location': LOCATION,
            'ip_configurations': [{
                'name': IP_CONFIG_NAME,
                'subnet': {
                    'id': subnet_info.id
                }
            }]
        }
    )
    return async_nic_creation.result()

def create_vm_parameters(nic_id, vm_reference,VM_NAME,USERNAME,PASSWORD,LOCATION):
    """Create the VM parameters structure.
    """

    return {
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': USERNAME,
            'admin_password': PASSWORD
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1_v2'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': vm_reference['publisher'],
                'offer': vm_reference['offer'],
                'sku': vm_reference['sku'],
                'version': vm_reference['version']
            },
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic_id,
            }]
        },
    }









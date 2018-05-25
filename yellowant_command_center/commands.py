"""Code which actually takes care of application API calls or other business logic"""
from yellowant.messageformat import MessageClass
from azure.mgmt.resource import ResourceManagementClient
from todo.sdk import TodoSDK
from yellowant_message_builder.messages import items_message, item_message
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.common.credentials import UserPassCredentials

import os
import traceback

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption

from msrestazure.azure_exceptions import CloudError

from haikunator import Haikunator
# def create_vm(args,user_integration,message=None):

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
    delete_async_operation.wait()
    print("Resource group has been deleted")
    message.message_text = "Your resource group has been deleted"
    return message


def create_vm(args,user_integration):
    global GROUP_NAME,VM_NAME,USERNAME,PASSWORD

    message = MessageClass()
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)
    GROUP_NAME = args.get("Resource-Group")
    VM_NAME = args.get("VM-Name")
    NIC_NAME = args.get("nic_name")
    IP_CONFIG_NAME = args.get("ipconfig_name")
    USERNAME = args.get("username")
    PASSWORD = args.get("password")
    VNET_NAME = args.get("vnet_name")
    SUBNET_NAME = args.get("subnet_name")



    try:
        # Create a NIC
        nic = create_nic(network_client,VNET_NAME,SUBNET_NAME,IP_CONFIG_NAME,NIC_NAME)

        #############
        # VM Sample #
        #############

        # Create Linux VM
        print('\nCreating Linux Virtual Machine')
        vm_parameters = create_vm_parameters(nic.id, VM_REFERENCE['linux'],VM_NAME,USERNAME,PASSWORD)
        async_vm_creation = compute_client.virtual_machines.create_or_update(
            GROUP_NAME, VM_NAME, vm_parameters)
        #async_vm_creation.wait()
        message.message_text = "You are Virtual Machine is being created"

    except CloudError:
        print('A VM operation failed:', traceback.format_exc(), sep='\n')
        message.message_text = "There was an error.Please try again"

    else:
        print('All example operations completed successfully!')

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
    async_vm_start.wait()

    message.message_text = "VM started"

    return message

def stop_vm(args , user_integration):
    GROUP_NAME=args.get('group_name')
    VM_NAME=args.get('vm_name')
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)

    print('\nStop VM')
    async_vm_stop = compute_client.virtual_machines.power_off(GROUP_NAME, VM_NAME)
    async_vm_stop.wait()
    message.message_text = "VM stopped"

    return message

def restart_vm(args , user_integration):
    GROUP_NAME=args.get('group_name')
    VM_NAME=args.get('vm_name')
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    # Restart the VM
    print('\nRestart VM')
    async_vm_restart = compute_client.virtual_machines.restart(GROUP_NAME, VM_NAME)
    async_vm_restart.wait()
    message.message_text = "VM Restarted"

    return message

def list_all_vms(args , user_integration):
    message = MessageClass()
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    print('\nList VMs in subscription')
    for vm in compute_client.virtual_machines.list_all():
        print("\tVM: {}".format(vm.name))
    message.message_text = "Listing all VMs"

    return message

def list_all_vms_in_rg(args,user_integration):
    message = MessageClass()
    GROUP_NAME = args.get("Resource-Group")
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    print('\nList VMs in resource group')
    for vm in compute_client.virtual_machines.list(GROUP_NAME):
        print("\tVM: {}".format(vm.name))
    message.message_text = "Listing all VMs"

    return message



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
    async_disk_attach.wait()
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

#=======================================================================================================================

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

def create_vm_parameters(nic_id, vm_reference,VM_NAME,USERNAME,PASSWORD):
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
###########################################################################################################################################
def create_item(args, user_integration, message=None):
    message = message or MessageClass()

    # verify arguments
    title = args.get("title")
    description = args.get("description")
    if title is None or len(title) == 0:
        # inform the user that they have not provided valid arguments
        message.message_text = "You need to provide values for both `title` and `description` as arguments."
        return message

    new_item = TodoSDK(token=user_integration.user.id).create_item(title=title, description=description)

    # build return message for the user
    message.message_text = "You have created a new item:"
    message = item_message(new_item, user_integration, message)

    return message


def get_list(args, user_integration, message=None):
    message = message or MessageClass()

    todo_list = TodoSDK(token=user_integration.user.id).get_list()

    # inform the user if the todo list is empty
    if len(todo_list) == 0:
        message.message_text = "Your todo list is empty"
        return message

    # create message with the list of todos
    message.message_text = "Here are your todo items:"
    message = items_message(todo_list, user_integration, message)
    return message


def get_item(args, user_integration, message=None):
    message = message or MessageClass()

    # verify args
    try:
        # since an item's id is supposed to be an integer, we will try casting the argument `id` to an int
        item_id = int(args.get("id"))
    except:
        # inform the user that they need to provide a valid integer id
        message.message_text = "You need to provide an integer value for the argument `id`."
        return message

    # inform the user if the item was not found by the id
    try:
        item = TodoSDK(token=user_integration.user.id).get_item(id=item_id)
        # create message for the found item
        message.message_text = "Here are the item details:"
        message = item_message(item, user_integration, message)
    except:
        message.message_text = "Could not find todo item with the id: {}".format(item_id)

    return message


def update_item(args, user_integration, message=None):
    message = message or MessageClass()

    # verify args
    title = args.get("title")
    description = args.get("description")
    try:
        # since an item's id is supposed to be an integer, we will try casting the argument `id` to an int
        item_id = int(args.get("id"))
    except:
        # inform the user that they need to provide a valid integer id
        message.message_text = "You need to provide an integer value for the argument `id`."
        return message

    try:
        updated_item = TodoSDK(token=user_integration.user.id).update_item(id=item_id, title=title, description=description)
        # create message with the updated item
        message.message_text = "Here are the updated item details:"
        message = item_message(updated_item, user_integration, message)
    except:
        message.message_text = "Could not find todo item with the id: {}".format(item_id)

    return message


def delete_item(args, user_integration, message=None):
    message = message or MessageClass()

    # verify args
    try:
        # since an item's id is supposed to be an integer, we will try casting the argument `id` to an int
        item_id = int(args.get("id"))
    except:
        # inform the user that they need to provide a valid integer id
        message.message_text = "You need to provide an integer value for the argument `id`."
        return message

    try:
        todo_list = TodoSDK(token=user_integration.user.id).delete_item(id=item_id)
        # create message with the list of todos
        if len(todo_list) == 0:
            message.message_text = "Your todo list is empty."
        else:
            message.message_text = "Here are your todo items:"
            message = items_message(todo_list, user_integration, message)
        return message
    except:
        message.message_text = "Could not find todo item with the id: {}".format(item_id)

    return message
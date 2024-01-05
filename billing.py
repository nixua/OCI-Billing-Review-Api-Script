#!/usr/bin/env python3
import code
from oci import util
from typing import *
from datetime import datetime, timezone, timedelta
import oci
import zoneinfo
import sys
  
  

#######################
#     BASIC CONFIG    #
#######################
# ~/.oci/config
config = oci.config.from_file()
print (config)
tz = zoneinfo.ZoneInfo('Europe/Paris')
now_paris = datetime.now(tz)
print(now_paris)
identity_client = oci.identity.IdentityClient(config=config)
compute_client = oci.core.ComputeClient(config=config)
  
  

#######################
#        UTILS        #
#######################
#Adding counters for each category of resources
total_compartment = 0
total_instances = 0
total_vcns = 0
total_block_storage_att = 0
total_block_storage_unatt = 0
total_boot_volumes = 0
total_boot_volume_backups = 0
total_volume_group = 0
total_volume_group_backup = 0
total_volume_backups = 0
total_bucket = 0
total_autonomous_dbs = 0
total_pluggable_dbs = 0
total_db_systems = 0
total_simple_dbs = 0
  
 
#Function to retrieve Tenant namespace
def get_namespace():
    object_storage_client = oci.object_storage.ObjectStorageClient(config=config)
    try:
        namespace = object_storage_client.get_namespace().data
        print(f'OCI Namespace: {namespace}')
        return namespace
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving namespace: {e}")
  
 
#Function to calculate the difference in days
def check_time_diff(created_time, threshold_days):
    current_time = datetime.now(timezone.utc)
    difference = current_time - created_time
    return difference.days > threshold_days
  
 
 
#######################
# GET RESSOURCES FNCT #
#######################
#Function to retrieve all compartments recursively
def get_all_compartments(compartment_id, compartments=[]):
    global total_compartment
    if compartments == []:
        starting_compartment = identity_client.get_compartment(compartment_id).data
        compartments.append(starting_compartment)
    sub_compartments = oci.pagination.list_call_get_all_results(
        identity_client.list_compartments,
        compartment_id=compartment_id,
        lifecycle_state=oci.identity.models.Compartment.LIFECYCLE_STATE_ACTIVE
    ).data
    for compartment in sub_compartments:
        total_compartment += 1
        compartments.append(compartment)
        get_all_compartments(compartment.id, compartments)
    return compartments


#Instance listing function
def list_instances(compartment_id, threshold_days):
    try:
        instances = oci.pagination.list_call_get_all_results(
            compute_client.list_instances, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), instances))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving instances for compartment {compartment_id}: {e}")
  
 
def print_instances(instances):
    global total_instances
    for instance in instances:
        total_instances += 1
        print(f'    - Instance ID: {instance.id}')
        print(f'    - Instance Name: {instance.display_name}')
        print(f'    - Instance State: {instance.lifecycle_state}')
        print(f'    - Creation Date: {instance.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_vcns(compartment_id, threshold_days):
    virtual_network_client = oci.core.VirtualNetworkClient(config=config)
    try:
        vcns = oci.pagination.list_call_get_all_results(
            virtual_network_client.list_vcns, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), vcns))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving VCNs for compartment {compartment_id}: {e}")
  
 
def print_vcns(vcns):
    global total_vcns
    for vcn in vcns:
        total_vcns += 1
        print(f'    - VCN ID: {vcn.id}')
        print(f'    - VCN Name: {vcn.display_name}')
        print(f'    - VCN CIDR Block: {vcn.cidr_block}')
        print(f'    - Creation Date: {vcn.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_block_storages(compartment_id, threshold_days):
    block_storage_client = oci.core.BlockstorageClient(config=config)
    try:
        all_volumes = oci.pagination.list_call_get_all_results(
            block_storage_client.list_volumes, compartment_id=compartment_id
        ).data
        all_volumes = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), all_volumes))
        attached_volumes = oci.pagination.list_call_get_all_results(
            compute_client.list_volume_attachments, compartment_id=compartment_id
        ).data
        attached_volume_ids = [attachment.volume_id for attachment in attached_volumes]
  
        return (all_volumes, attached_volumes, attached_volume_ids)
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving block storages for compartment {compartment_id}: {e}")
  
 
def print_block_storages(all_volumes, attached_volumes, attached_volume_ids):
    block_storage_client = oci.core.BlockstorageClient(config=config)
    global total_block_storage_att
    global total_block_storage_unatt
    for volume in all_volumes:
        if volume.id in attached_volume_ids:
            total_block_storage_att += 1
            status = "Attached"
        else:
            total_block_storage_unatt += 1
            status = "Unattached"
        print(f'    - Block Storage ID: {volume.id}')
        print(f'    - Name: {volume.display_name}')
        print(f'    - Size in GBs: {volume.size_in_gbs}')
        print(f'    - Status: {status}')
        print(f'    - Lifecycle State: {volume.lifecycle_state}')
        print(f'    - Creation Date: {volume.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_boot_volumes(compartment_id, threshold_days):
    block_storage_client = oci.core.BlockstorageClient(config=config)
    try:
        boot_volumes = oci.pagination.list_call_get_all_results(
            block_storage_client.list_boot_volumes, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), boot_volumes))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving boot volumes for compartment {compartment_id}: {e}")
  

def print_boot_volumes(boot_volumes):
    global total_boot_volumes
    for boot_volume in boot_volumes:
        total_boot_volumes += 1
        print(f'    - Boot Volume ID: {boot_volume.id}')
        print(f'    - Name: {boot_volume.display_name}')
        print(f'    - Size in GBs: {boot_volume.size_in_gbs}')
        print(f'    - Lifecycle State: {boot_volume.lifecycle_state}')
        print(f'    - Creation Date: {boot_volume.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_boot_volume_backups(compartment_id, threshold_days):
    block_storage_client = oci.core.BlockstorageClient(config=config)
    try:
        boot_volume_backups = oci.pagination.list_call_get_all_results(
            block_storage_client.list_boot_volume_backups, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), boot_volume_backups))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving boot volume backups for compartment {compartment_id}: {e}")
  
 
def print_boot_volume_backups(boot_volume_backups):
    global total_boot_volume_backups
    for backup in boot_volume_backups:
        total_boot_volume_backups += 1
        print(f'    - Boot Volume Backup ID: {backup.id}')
        print(f'    - Name: {backup.display_name}')
        print(f'    - Size in GBs: {backup.size_in_gbs}')
        print(f'    - Lifecycle State: {backup.lifecycle_state}')
        print(f'    - Creation Date: {backup.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_volume_groups(compartment_id, threshold_days):
    block_storage_client = oci.core.BlockstorageClient(config=config)
    try:
        volume_groups = oci.pagination.list_call_get_all_results(
            block_storage_client.list_volume_groups, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), volume_groups))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving volume groups for compartment {compartment_id}: {e}")
  
 
def print_volume_groups(volume_groups):
    global total_volume_group
    for group in volume_groups:
        total_volume_group += 1
        print(f'    - Volume Group ID: {group.id}')
        print(f'    - Name: {group.display_name}')
        print(f'    - Size in GBs: {group.size_in_gbs}')
        print(f'    - Lifecycle State: {group.lifecycle_state}')
        print(f'    - Creation Date: {group.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_volume_group_backups(compartment_id, threshold_days):
    block_storage_client = oci.core.BlockstorageClient(config=config)
    try:
        volume_group_backups = oci.pagination.list_call_get_all_results(
            block_storage_client.list_volume_group_backups, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), volume_group_backups))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving volume group backups for compartment {compartment_id}: {e}")
  
 
def print_volume_group_backups(volume_group_backups):
    global total_volume_group_backup
    for backup in volume_group_backups:
        total_volume_group_backup += 1
        print(f'    - Volume Group Backup ID: {backup.id}')
        print(f'    - Name: {backup.display_name}')
        print(f'    - Size in GBs: {backup.size_in_gbs}')
        print(f'    - Lifecycle State: {backup.lifecycle_state}')
        print(f'    - Creation Date: {backup.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_volume_backups(compartment_id, threshold_days):
    block_storage_client = oci.core.BlockstorageClient(config=config)
    try:
        volume_backups = oci.pagination.list_call_get_all_results(
            block_storage_client.list_volume_backups, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), volume_backups))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving volume backups for compartment {compartment_id}: {e}")
  
def print_volume_backups(volume_backups):
    global total_volume_backups
    for backup in volume_backups:
        total_volume_backups += 1
        print(f'    - Volume Backup ID: {backup.id}')
        print(f'    - Name: {backup.display_name}')
        print(f'    - Size in GBs: {backup.size_in_gbs}')
        print(f'    - Lifecycle State: {backup.lifecycle_state}')
        print(f'    - Creation Date: {backup.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_autonomous_databases(compartment_id, threshold_days):
    db_client = oci.database.DatabaseClient(config=config)
    try:
        autonomous_databases = oci.pagination.list_call_get_all_results(
            db_client.list_autonomous_databases, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), autonomous_databases))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving autonomous databases for compartment {compartment_id}: {e}")
  
 
def print_autonomous_databases(autonomous_dbs):
    global total_autonomous_dbs
    for adb in autonomous_dbs:
        total_autonomous_dbs += 1
        print(f'    - Autonomous Database ID: {adb.id}')
        print(f'    - Autonomous Database Name: {adb.db_name}')
        print(f'    - Autonomous Database Version: {adb.db_version}')
        print(f'    - Autonomous Database Workload: {adb.db_workload}')
        print(f'    - Autonomous Database Lifecycle State: {adb.lifecycle_state}')
        print(f'    - Autonomous Database Creation Date: {adb.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()

 
 
def list_pluggable_databases(compartment_id, threshold_days):
    db_client = oci.database.DatabaseClient(config=config)
    try:
        pluggable_databases = oci.pagination.list_call_get_all_results(
            db_client.list_pluggable_databases, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), pluggable_databases))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving pluggable databases for compartment {compartment_id}: {e}")
  
 
def print_pluggable_databases(pluggable_dbs):
    global total_pluggable_dbs
    for pdb in pluggable_dbs:
        total_pluggable_dbs += 1
        print(f'    - Pluggable Database ID: {pdb.id}')
        print(f'    - Pluggable Database Lifecycle State: {pdb.lifecycle_state}')
        print(f'    - Pluggable Database Creation Date: {pdb.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def list_db_systems(compartment_id, threshold_days):
    db_client = oci.database.DatabaseClient(config=config)
    try:
        db_systems = oci.pagination.list_call_get_all_results(
            db_client.list_db_systems, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), db_systems))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving DB Systems for compartment {compartment_id}: {e}")
  

def print_db_systems(db_systems):
    global total_db_systems
    for db_system in db_systems:
        total_db_systems += 1
        print(f'    - System DB ID: {db_system.id}')
        print(f'    - System DB Name: {db_system.display_name}')
        print(f'    - System DB Version: {db_system.version}')
        print(f'    - System DB Edition: {db_system.database_edition}')
        print(f'    - System DB Lifecycle State: {db_system.lifecycle_state}')
        print(f'    - System DB Creation Date: {db_system.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()


 
def list_simple_databases(compartment_id, threshold_days):
    database_client = oci.database.DatabaseClient(config=config)
    try:
        database_list = []
        db_homes = oci.pagination.list_call_get_all_results(
            database_client.list_db_homes, compartment_id=compartment_id
        ).data
        for db_home in db_homes:
            databases = oci.pagination.list_call_get_all_results(
                database_client.list_databases, compartment_id=compartment_id, db_home_id=db_home.id
            ).data
            for db in databases:
                if check_time_diff(db.time_created, threshold_days):
                    database_list.append(db)
        return database_list
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving simple databases for compartment {compartment_id}: {e}")
  
def print_simple_databases(databases):
    global total_simple_dbs
    for db in databases:
        total_simple_dbs += 1
        print(' - Simple Database ID: {}'.format(db.id))
        print(' - Simple DB Name: {}'.format(db.db_name))
        print(' - Simple DB Lifecycle State: {}'.format(db.lifecycle_state))
        print(' - Simple DB Creation Date: {}'.format(db.time_created.strftime('%Y-%m-%d %H:%M:%S')))
        print()

 
 
def list_buckets(namespace_name, compartment_id, threshold_days):
    object_storage_client = oci.object_storage.ObjectStorageClient(config=config)
    try:
        buckets = oci.pagination.list_call_get_all_results(
            object_storage_client.list_buckets, namespace_name=namespace_name, compartment_id=compartment_id
        ).data
        l = list(filter(lambda x: check_time_diff(x.time_created, threshold_days), buckets))
        return l
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving buckets for compartment {compartment_id}: {e}")
  
 
def print_buckets(buckets):
    global total_bucket
    for bucket in buckets:
        total_bucket+=1
        print(f'    - Bucket Name: {bucket.name}')
        print(f'    - Creation Date: {bucket.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
  
 
def print_html_buckets(buckets):
    global total_bucket
    print('<table>')
    for bucket in buckets:
        total_bucket+=1
        print('<tr>')
        print(f'<td>Bucket Name: {bucket.name}</td>')
        print(f'<td>Creation Date: {bucket.time_created.strftime("%Y-%m-%d %H:%M:%S")}</td>')
        print('</tr>')
    print('</table>')
  
 
 
#######################
#    CALL MAIN FNCT   #
#######################
#Main script to display the ressources
def main():
    #Define Datediff
    try:
        threshold_days = int(sys.argv[1])
    except:
        print('Usage: {} <threshold days>'.format(sys.argv[0]))
        sys.exit(1)
  
    #Get Namespace from previous function
    namespace = get_namespace()  
    if namespace is None:
        return
    root_compartment_id = config
    all_compartments = get_all_compartments(config["tenancy"])

  
 
        #Calling functions to list resources
        instances = list_instances(compartment.id, threshold_days)
        vcns = list_vcns(compartment.id, threshold_days)
        all_volumes, attached_volumes, attached_volume_ids = list_block_storages(compartment.id, threshold_days)
        boot_volumes = list_boot_volumes(compartment.id, threshold_days)
        boot_volume_backups = list_boot_volume_backups(compartment.id, threshold_days)
        volume_groups = list_volume_groups(compartment.id, threshold_days)
        volume_group_backups = list_volume_group_backups(compartment.id, threshold_days)
        volume_backups = list_volume_backups(compartment.id, threshold_days)
        autonomous_databases = list_autonomous_databases(compartment.id, threshold_days)
        pluggable_databases = list_pluggable_databases(compartment.id, threshold_days)
        db_systems = list_db_systems(compartment.id, threshold_days)
        simple_databases = list_simple_databases(compartment.id, threshold_days)
        buckets = list_buckets(namespace, compartment.id, threshold_days)
  
 
        if len(instances) == 0 and len(all_volumes) == 0 and len(boot_volumes) == 0 and len(boot_volume_backups) == 0 and len(volume_groups) == 0 and len(volume_group_backups) == 0 and len(volume_backups) == 0 and len(autonomous_databases) == 0 and len(pluggable_databases) == 0 and len(db_systems) == 0 and len(simple_databases) == 0 and len(buckets) == 0:
            pass
        else:
            print(f'Compartment ID: {compartment.id}')
            print(f'  - Compartment name: {compartment.name}')
            print(f'  - Creation Date: {compartment.time_created.strftime("%Y-%m-%d %H:%M:%S")}')
            print()
            print('-' * 200)
            print()
  
            print_instances(instances)
            print_vcns(vcns)
            print_block_storages(all_volumes, attached_volumes, attached_volume_ids)
            print_boot_volumes(boot_volumes)
            print_boot_volume_backups(boot_volume_backups)
            print_volume_groups(volume_groups)
            print_volume_group_backups(volume_group_backups)
            print_volume_backups(volume_backups)
            print_autonomous_databases(autonomous_databases)
            print_pluggable_databases(pluggable_databases)
            print_db_systems(db_systems)
            print_simple_databases(simple_databases)
            print_buckets(buckets)

 
    #Print results
    print(f"Total Compartments: {total_compartment}")
    print(f"Total Instances: {total_instances}")
    print(f"Total VCNS: {total_vcns}")
    print(f"Total Block Storage Attached: {total_block_storage_att}")
    print(f"Total Block Storage Unattached: {total_block_storage_unatt}")
    print(f"Total Boot Volumes: {total_boot_volumes}")
    print(f"Total Boot Volumes Backup: {total_boot_volume_backups}")
    print(f"Total Volumes Groups: {total_volume_group}")
    print(f"Total Volumes Groups Backup: {total_volume_group_backup}")
    print(f"Total Volumes Backup: {total_volume_backups}")
    print(f"Total Autonomous DBs: {total_autonomous_dbs}")
    print(f"Total Pluggable DBs: {total_pluggable_dbs}")
    print(f"Total System DBs: {total_db_systems}")
    print(f"Total Simple DBs: {total_simple_dbs}")
    print(f"Total Buckets: {total_bucket}")
  
#Call Main  
main()
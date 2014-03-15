#!/usr/bin/env python
import parted
import pickle;

# get all devices on system
devices = parted.getAllDevices();

# create something like:
#dict['/dev/sdb']= {'size' : 1000};
#                  {'fs'   : ext3};

disk_array={};

def get_device_information(devices):
    global disk_array;
    # list attaced devices
    for device in devices:
        # only list devices with type 1 = real hard disk
        # mapper device would be type 12
        if device.type == 1:
            geom = device.hardwareGeometry
            ssize= device.sectorSize
            #38913 * 255 * 63 * 512 = disk size
            size = (geom[0] * geom[1] * geom[2] * ssize) / 1000 / 1000 / 1000;
            disk_array[device.path] = {};
            disk_array[device.path]['model'] = device.model;
            disk_array[device.path]['size'] = size;
            disk_array[device.path]['cylinders'] = geom[0];
            disk_array[device.path]['heads'] = geom[1];
            disk_array[device.path]['sectors'] = geom[2];
            disk_array[device.path]['sector_size'] = ssize;
            disk_array[device.path]['partitions'] = {};

def get_partition_information(devices):
    global disk_array;
    for device in devices:
        if device.type == 1:
            disk = parted.Disk(device)
            primary_partitions=disk.getPrimaryPartitions()
            logical_partitions=disk.getLogicalPartitions()
            extended_partition=disk.getExtendedPartition()

            for partition in primary_partitions:
                disk_array[device.path]['partitions'][partition.path] = {};
                disk_array[device.path]['partitions'][partition.path]['size'] = partition.getSize(unit="b");
                try:
                    fs=parted.probeFileSystem(partition.geometry)
                except:
                    fs='none'
                disk_array[device.path]['partitions'][partition.path]['fs'] = fs;
                disk_array[device.path]['partitions'][partition.path]['first_block'] = partition.geometry.start;
                disk_array[device.path]['partitions'][partition.path]['end_block'] = partition.geometry.end;
                disk_array[device.path]['partitions'][partition.path]['length'] = partition.geometry.end;
                disk_array[device.path]['partitions'][partition.path]['type'] = 'primary';

            if extended_partition:
                disk_array[device.path]['partitions'][extended_partition.path] = {};
                disk_array[device.path]['partitions'][extended_partition.path]['size'] = extended_partition.getSize(unit="b");
                try:
                    fs=parted.probeFileSystem(extended.partition.geometry)
                except:
                    fs='none'
                disk_array[device.path]['partitions'][extended_partition.path]['fs'] = fs;
                disk_array[device.path]['partitions'][extended_partition.path]['first_block'] = extended_partition.geometry.start;
                disk_array[device.path]['partitions'][extended_partition.path]['end_block'] = extended_partition.geometry.end;
                disk_array[device.path]['partitions'][extended_partition.path]['length'] = extended_partition.geometry.end;
                disk_array[device.path]['partitions'][extended_partition.path]['type'] = 'extended';


            for partition in logical_partitions:
                disk_array[device.path]['partitions'][partition.path] = {};
                disk_array[device.path]['partitions'][partition.path]['size'] = partition.getSize(unit="b");
                try:
                    fs=parted.probeFileSystem(partition.geometry)
                except:
                    fs='none'
                disk_array[device.path]['partitions'][partition.path]['fs'] = fs;
                disk_array[device.path]['partitions'][partition.path]['first_block'] = partition.geometry.start;
                disk_array[device.path]['partitions'][partition.path]['end_block'] = partition.geometry.end;
                disk_array[device.path]['partitions'][partition.path]['length'] = partition.geometry.end;
                disk_array[device.path]['partitions'][partition.path]['type'] = 'logical';



def print_information(disk_array):
    print "Found Hardware Devices:"
    print "-----------------------"
    for disks in sorted(disk_array.iterkeys()):
        print "%s" % disks
        print "     model: %s" % disk_array[disks]['model'];
        print "     size:  %s GB (Cylinders: %s, Heads: %s, Sectors: %s, Sector Size: %s)" % (
                    disk_array[disks]['size'],
                    disk_array[disks]['cylinders'],
                    disk_array[disks]['heads'],
                    disk_array[disks]['sectors'],
                    disk_array[disks]['sector_size']);
    print "-----------------------"

    print "Found Partitions on Hardware Devices:"
    print "-----------------------"
    for disks in sorted(disk_array.iterkeys()):
        print "%s" % disks
        for partition in sorted(disk_array[disks]['partitions'].iterkeys()):
            print " %s" % partition;
            print "     size:        %s" % disk_array[disks]['partitions'][partition]['size'];
            print "     fs:          %s" % disk_array[disks]['partitions'][partition]['fs'];
            print "     first block: %s" % disk_array[disks]['partitions'][partition]['first_block'];
            print "     end block:   %s" % disk_array[disks]['partitions'][partition]['end_block'];
            print "     length:      %s" % disk_array[disks]['partitions'][partition]['length'];
            print "     type:        %s" % disk_array[disks]['partitions'][partition]['type'];
            print "     parted:      parted --script -m %s mkpart %s %s %s" % (
                                                        disks,
                                                        disk_array[disks]['partitions'][partition]['type'],
                                                        disk_array[disks]['partitions'][partition]['first_block'],
                                                        disk_array[disks]['partitions'][partition]['end_block']
                                                        );
    print "-----------------------"
#mkpart PART-TYPE FS-TYPE START END


get_device_information(devices);
get_partition_information(devices);

#save disk array to pickle layout
output = open('disk_array.pk1', 'wb')
pickle.dump(disk_array,output);
output.close()

# load disk array from pickle layout

input = open('disk_array.pk1','rb')
new_array = pickle.load(input);
input.close()

print_information(disk_array);

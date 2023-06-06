# NetBackup for dummies

The following guide aims at listing helpful commands, resources and steps for
various NetBackup tasks

## Environment

It is assumed that the following variables have been defined with the
appropriate values:

```bash
MASTER_SERVER='<master server hostname>'
MEDIA_SERVER='<media server hostname>'
CLIENT='<client hostname>'
```

The following values should also be added to the `$PATH` variable:

```bash
PATH="$PATH:/usr/openv/netbackup/bin/admincmd:/usr/openv/netbackup/bin:/usr/openv/volmgr/bin"
```

## Existing resources

The following [cheatsheet](http://www.datadisk.co.uk/html_docs/veritas/veritas_netbackup_cs.htm)
gives a list of interesting examples of commands and tool uses offered with the
NetBackup product.

Below some other examples interesting from a security point of view.

## Definitions

## Backup policy

Definition containing the list of files to backup, the clients targeted, the
frequency of backups, and more

### Storage Lifecycle Policies (SLP)

Storage Plan for a set of backup which determines how the data is stored,
copied, replicated, and retained

### Storage Unit

Location where data is stored

### Backup image

A backup image stores all items backed-up in one job. Each image is related to
a backup policy and a server, and is assigned a backup id

### Backup image copy

An image can have multiple copies

### Backup image copy fragment

A copy can be split in multiple fragments, each fragment located on a media
server

## Listing clients

On the master server:

```bash
# List all clients
$ bpplclients -allunique -U
```

## Listing client backups

On the master server:

```bash
# List backups from the last 48 hours
$ bpimagelist -hoursago 48 -client "$BACKUP"
```

## Viewing backup policies

On the master server:

```bash
# List all backup policies
$ bppllist -allpolicies -L

# Display information of a backup policy
$ bppllist <policy_name> -U -L

# Display all backup policy for a specific client
$ bppllist -byclient "$CLIENT" -U
```

## Viewing scheduled backups

On the master server:

```bash
$ nbpemreq -predict_all -date 02/10/2021 23:59:59
```

## Listing files from a backup policy

On the master server:

```bash
# List all backup policy names
$ bppllist -allpolicies -L | grep "Policy Name:"

# List all explicitely included paths
$ bppllist <policy_name> | grep INCLUDE | cut -d' ' -f2

# Some more contents
$ bplist -C "$CLIENT" -R "/root"
```

## Listing Storage Lifecycle Policies

On the master server:

```bash
# Display all STLs
$ nbstlutil list

# Display information about a backupid
$ nbstlutil list -backupid <id> -U

# Display information about a client
$ nbstlutil list -client "$CLIENT" -U
```

More details: <https://www.veritas.com/support/en_US/article.100006475>

## Viewing storage units

On the master server:

```bash
# List all storage unit
$ bpstulist -L

# Display information about a specific storage unit
$ bpstulist -label <storage_unit_name> -U
```

## Viewing volume pools

On the master server:

```bash
# List volume pools
$ vmpool -listall

# List media needed for a specific pool
$ vmquery -h "$MEDIA_SERVER" -pn <pool_name>
```

## Finding client versions

On the master server:

### Linux

```bash
while read x; do echo "$x : $(bpgetconfig -g $x | tail -n +3 | head -n 1)" >> /tmp/agent.txt; done < <(bpplclients -allunique -U | tr -s ' ' | tail -n +3 | cut -d' ' -f3)
```

### Windows

```powershell
bpplclients -allunique -U | Select-Object -skip 3 | ForEach-Object {$_.Substring(44) + " : " + "$(bpgetconfig -g $_.Substring(44) | Select-Object -Index 2)"}
```

## Finding what is backed up for a specific host

On the master server:

```bash
$ bpflist -U -client "$CLIENT" -rl 100
```

## List all Storage Policies for a client

On the master server:

```bash
$ nbstlutil list -client "$CLIENT" -U
```

## Restoring a backup

### Unique file

#### Create a rename file

The rename file contains a mapping between restored files and location to which
to restore the file (do not forget the `\n` at the end)

```bash
$ cat rename_file
change /etc/shadow to /tmp/stolen
```

#### Restore files

```bash
$ bprestore -C "$CLIENT" -D "$MEDIA_SERVER" -K -R ./rename_file /etc/shadow
```

### Folder

```bash
$ cat rename_file
change /home/user to /tmp/stolen

$ bprestore -C "$CLIENT" -D "$MEDIA_SERVER" -K -R ./rename_file /home/user
```

## Creating a backup for a client

Main source: <https://vox.veritas.com/t5/NetBackup/Creating-a-backup-policy-from-cli/td-p/415780>

### Create storage

1. Create a storage server (on the master server)

   ```bash
   $ nbdevconfig -creatests -storage_server "$MEDIA_SERVER" -stype AdvancedDisk -st 5 -media_server "$MEDIA_SERVER"
   Storage server nb-media-a has been successfully created
   $ nbdevquery -liststs -u
   Storage Server      : nb-media-a
   Storage Server Type : AdvancedDisk
   Storage Type        : Formatted Disk, Direct Attached
   State               : UP
   Flag                : OpenStorage
   Flag                : AdminUp
   Flag                : InternalUp
   Flag                : SpanImages
   Flag                : LifeCycle
   Flag                : CapacityMgmt
   Flag                : FragmentImages
   Flag                : Cpr
   Flag                : RandomWrites
   Flag                : FT-Transfer
   Flag                : CapacityManagedRetention
   Flag                : CapacityManagedJobQueuing
   ```
2. Create volume (on the media server). Note that the volume needs to be a mount
   point, not a folder

   ```bash
   $ mkdir /root/volume /mnt/volume
   $ mount -o bind /root/volume /mnt/volume
   ```
3. Create a disk pool (on the master server)

   ```bash
   # First list available volumes
   $ nbdevconfig -previewdv -storage_server "$MEDIA_SERVER" -stype AdvancedDisk
   V_5_ DiskVolume < "/mnt/volume" "/mnt/volume" 53660876800 37310164992 0 0 0 0 0 0 0 >
   V_5_ DiskVolume < "/run/user/0" "/run/user/0" 192712704 192712704 0 0 0 0 0 0 0 >
   V_5_ DiskVolume < "/home" "/home" 50432839680 50398937088 0 0 0 0 0 0 0 >
   ...

   # Select the one you want in a file, here the first one
   $ nbdevconfig -previewdv -storage_server "$MEDIA_SERVER" -stype AdvancedDisk | head -n 1 | tee /root/dvlist.txt
   V_5_ DiskVolume < "/mnt/volume" "/mnt/volume" 53660876800 37310164992 0 0 0 0 0 0 0 >

   # Create a disk pool with the volumes you want
   $ nbdevconfig -createdp -dp airbusseclab_pool -stype AdvancedDisk -storage_servers "$MEDIA_SERVER" -dvlist /root/dvlist.txt
   Disk pool airbusseclab_pool has been successfully created with 1 volumes

   # List disk pool created
   $ nbdevquery -listdv -stype AdvancedDisk
   V_5_ airbusseclab_pool AdvancedDisk /mnt/volume @aaaac 49.98 34.75 30 1 0 1 0 0 14 0

   # List disk volumes available
   $ nbdevquery -listdp
   V7.5 airbusseclab_pool 1 49.98 49.98 1 98 80 -1 nb-media
   ```
4. Create a storage unit (on the master server)

   ```bash
   $ bpstuadd -label airbusseclab_stu -dt 6 -dp airbusseclab_pool -host "$MEDIA_SERVER"
   $ bpstulist
   airbusseclab_stu 0 nb-media-a 0 -1 -1 1 0 "*NULL*" 1 1 524288 nb-media-a 0 6 0 0 0 0 airbusseclab_pool nb-media-a 515527
   ```
5. Create a Storage Lifecycle Policy (on the master server, optional)

   ```bash
   $ nbstl airbusseclab_stl -add -residence airbusseclab_stu
   $ nbstl -L
                                   Name: airbusseclab_stl
                    Data Classification: (none specified)
               Duplication Job Priority: 0
                                  State: active
                                Version: 0
    Operation  1                Use for: 0 (backup)
                                Storage: airbusseclab_stu
                            Volume Pool: (none specified)
                           Server Group: (none specified)
                         Retention Type: 0 (Fixed)
                        Retention Level: 1 (2 weeks)
                  Alternate Read Server: (none specified)
                  Preserve Multiplexing: false
         Enable Automatic Remote Import: false
                                  State: active
                                 Source: 0 (client)
                           Operation ID: (none specified)
                        Operation Index: 1
                            Window Name: --
                    Window Close Option: --
                   Deferred Duplication: no
   ```

### Create backup

1. Create a backup policy (on the master server)

   1. Create a default backup policy

      ```bash
      $ bppolicynew airbusseclab_backup_policy
      $ bppllist airbusseclab_backup_policy -U
      ------------------------------------------------------------

      Policy Name:       airbusseclab_backup_policy

        Policy Type:         Standard
        Active:              yes
        Effective date:      06/02/2023 12:13:07
        Client Compress:     no
        Follow NFS Mounts:   no
        Cross Mount Points:  no
        Collect TIR info:    no
        Block Incremental:   no
        Mult. Data Streams:  no
        Client Encrypt:      no
        Checkpoint:          no
        Policy Priority:     0
        Max Jobs/Policy:     Unlimited
        Disaster Recovery:   0
        Collect BMR info:    no
        Residence:           (specific storage unit not required)
        Volume Pool:         NetBackup
        Server Group:        *ANY*
        Keyword:             (none specified)
        Data Classification:       -
        Residence is Storage Lifecycle Policy:    no
        Application Discovery:      no
        Discovery Lifetime:      0 seconds
        ASC Application and attributes: (none defined)

        Granular Restore Info:  no
        Ignore Client Direct:  no
        Use Accelerator:  no

        Clients:	(none defined)

        Include:	(none defined)

        Schedule:	(none defined)
      ```
   2. Update backup policy attributes

      ```bash
      $ bpplinfo airbusseclab_backup_policy -modify -residence airbusseclab_stu
      $ bppllist airbusseclab_backup_policy -U
      ------------------------------------------------------------

      Policy Name:       airbusseclab_backup_policy

        Policy Type:         Standard
        Active:              yes
        Effective date:      06/02/2023 12:13:07
        Client Compress:     no
        Follow NFS Mounts:   no
        Cross Mount Points:  no
        Collect TIR info:    no
        Block Incremental:   no
        Mult. Data Streams:  no
        Client Encrypt:      no
        Checkpoint:          no
        Policy Priority:     0
        Max Jobs/Policy:     Unlimited
        Disaster Recovery:   0
        Collect BMR info:    no
        Residence:           airbusseclab_stu
        Volume Pool:         NetBackup
        Server Group:        *ANY*
        Keyword:             (none specified)
        Data Classification:       -
        Residence is Storage Lifecycle Policy:    no
        Application Discovery:      no
        Discovery Lifetime:      0 seconds
        ASC Application and attributes: (none defined)

        Granular Restore Info:  no
        Ignore Client Direct:  no
        Use Accelerator:  no

        Clients:	(none defined)

        Include:	(none defined)

        Schedule:	(none defined)
      ````
   3. Add clients to that policy

      ```bash
      $ bpplclients -allunique -U
      Hardware         OS                         Client
      ---------------  -------------------------  --------------
      Linux            Centos                     nb-client-a-1
      $ bpplclients airbusseclab_backup_policy -add "$CLIENT" <Hardware> <OS>
      ```
   4. Add Backup selection

      ```bash
      # First create a list of path to backup
      $ echo "/etc/shadow" > tobackup.txt

      # Register this path
      $ bpplinclude airbusseclab_backup_policy -add -f tobackup.txt
      ```

   5. Add schedules

      ```bash
      $ bpplsched airbusseclab_backup_policy -add airbusseclab_schedule -freq 600 -st FULL
      ```
2. Launch a backup (on the client or on the master server)

   ```bash
   $ bpbackup -i -p airbusseclab_backup_policy -s airbusseclab_schedule -t 0
   ```

## Troubleshooting

Logs for admin commands, used while configuring backups, are located in
`/usr/openv/netbackup/logs/admin`.

Backup logs are accessible from the web UI on the master server
`https://<master server FQDN>/webui/jobs` or from the `bpjobd` logs in
`/usr/openv/netbackup/logs/bpjobd`.

Here are a few known issues and how to fix them.

### Clear host cache

```bash
/usr/openv/netbackup/bin/bpclntcmd -clear_host_cache
```

### No matching database entry found

If creating the storage server fails with the following error:

```
DSM has encountered an EMM error: No matching database entry found for: nb-media
```

Then it probably means that there is an issue with your `bp.conf` file, either
on the master server or on the media server.

On the master server, ensure you have the following attributes:

```
# Order is important, you only need one if master server = media server
SERVER = <your master server FQDN>
SERVER = <your media server FQDN>
CLIENT_NAME = <your master server FQDN>
MEDIA_SERVER = <your media server FQDN>
```

On the media server, ensure you have the following attributes:

```
# Order is important
SERVER = <your master server FQDN>
SERVER = <your media server FQDN>
CLIENT_NAME = <your media server FQDN>
MEDIA_SERVER = localhost
```

### Access to the client was not allowed

If backups fail and the web UI show the following status:

```
Access to the client was not allowed
```

The client's `bp.conf` file is most likely missing either the master server or
the media server, ensure you have the following attributes:

```
SERVER = <your master server FQDN>
SERVER = <your media server FQDN>
CLIENT_NAME = <your client FQDN>
```

### Disk volume is down

If backups fail and the web UI show the following status:

```
Disk volume is down
```

The media server is probably down, or the `/mnt/volume` folder is not mounted.

Restart the media server, mount the folder, and enter the following command:
```bash
$ nbdevconfig -changestate -stype server_type -dp disk_pool_name -dv disk_volume_name -state RESET
```

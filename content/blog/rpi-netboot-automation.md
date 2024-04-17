---
title: "Streamlining Raspberry Pi Deployment: A Guide to Automated Netbooting"
authorId: "rohit"
date: 2024-04-17
draft: true
featured: true
weight: 1
---

# Streamlining Raspberry Pi Deployment: A Guide to Automated Netbooting

## 1. Understanding Netbooting

### What is PXE Boot?
The Preboot Execution Environment (PXE) specification describes a standardized client–server environment that boots a software assembly retrieved from a network on PXE-enabled clients.

### Why PXE Boot?
- Simplify Pi provisioning and maintenance as much as possible.
- Automate updates/upgrades as much as possible.
- Netbooting is a good path to achieve this. For example, when you netboot a Pi, it does not require an SD card to boot. The OS and file system live on a central server. Because most of the provisioning happens on a central server, we can eventually automate it via scripts.

## 2. Setting Up the Infrastructure

### 2.1 Required Components
To implement netbooting for Raspberry Pi devices, you'll need the following components:
- Raspberry Pi units acting as PXE clients connected via Ethernet to the router or switch.
- Raspberry Pi or Odroid acting as a server containing boot files and user files connected via Ethernet to the router or switch.

### 2.2 Network Configuration

- **DHCP Server**: This server, often running on your router, assigns IP addresses to devices on your network. It handles static IP assignments and directs TFTP requests to the designated TFTP server.

- **TFTP Server**: Running on a separate device, typically an Odroid server, it manages the transfer of boot files necessary for the netbooting process. These files initiate the boot sequence on Raspberry Pi devices.

- **NFS Server**: Hosted on the Odroid server, the NFS server mounts the root file system for PXE clients (like Raspberry Pi devices), allowing access to necessary files and resources for network booting.

Furthermore, it's worth noting that in the absence of automation such as scripts, the process of setting up netbooting involves manual tasks. This includes copying the root files and boot files to specific directories based on the MAC address of each Raspberry Pi device.


## 3. Automation with Bash Scripting

In this section, we'll look into automating the netbooting process using a bash script (`pxeService.sh`) and an address list (`addresslist.txt`). The goal is to streamline the deployment and management of Raspberry Pi devices by automating the copying of necessary files and configurations.

### 3.1 Bash Script Overview

The `pxeService.sh` script is designed to automate the setup for each PXE client (Raspberry Pi device). Here's a breakdown of the script:

- #### Constants and Log Paths

```bash
#!/bin/bash
PORT=69
log_file_path="/var/log/pxeService.log"
LOG_FILE_PATH="/var/log/macscript.log"
```

In this code snippet, we define constants for the script, such as the UDP port to listen on and the paths for logging. Make sure to create `pxeService.log` and `macscript.log` in the `/var/log` directory.

- #### Handling Error and Listening to requests

```bash
handle_error() {
	echo "An error occurred at line $1" >> "$log_file_path"
	exit 1
}

trap 'handle_error $LINENO' ERR

tcpdump -l -i any -e udp port $PORT | while read line; do
	MAC=$(echo $line | awk '{print $6}' | tr ':' '-')
	TIME=$(date +"%Y-%m-%d %H:%M:%S")

	if grep -q "$MAC" /opt/addresslist.txt; then
    	echo "$MAC already exists" >> "$log_file_path"
	else
    	echo "************Executing macscript.sh for $MAC***************" >> "$log_file_path"
    	echo "$MAC" >> /opt/addresslist.txt

    	FILE=$(echo $line | grep -o -P '(?<=RRQ ")[^"]+')
    	FILE=$(awk -F'/' '{print $NF}' <<< "$FILE")

    	if [ "$FILE" = "start4.elf" ]; then
        	echo "Time: $TIME, MAC address: $MAC, Requested file: $FILE" >> "$log_file_path"
        	create_mac "$MAC" &
        	echo "**********macscript execution finished for mac $MAC**********" >> "$log_file_path"
    	else
        	echo "Not found" >> "$log_file_path"
    	fi
	fi
done
```

In this code snippet `handle_error` function, logs errors to the specified path, and uses `tcpdump` to listen to requests continuously. It checks whether the MAC address is in the address list and executes the `create_mac` function if necessary.

- #### Configure dnsmasq.conf

```bash
configure_dnsmasq() {
    local service_name="$1"

    if [ "$service_name" == "dnsmasq" ]; then
        if systemctl list-unit-files --type=service | grep -q "^dnsmasq.service"; then
            echo "Configuring dnsmasq.conf..."
            read -p "Enter the interface name (e.g., bond0): " interface_name
            cat <<EOF | sudo tee -a /etc/dnsmasq.conf > /dev/null
interface=$interface_name
no-hosts
enable-tftp
tftp-root=/srv/tftp
tftp-unique-root=mac
log-facility=/var/log/dnsmasq
port=5353
EOF
            echo "Configuration has been added to /etc/dnsmasq.conf"  >> "$LOG_FILE_PATH"
        fi
    fi
}
```

The `configure_dnsmasq` function sets the configurations for TFTP using dnsmasq. It prompts the user to enter the interface name, adds the specified configurations to `/etc/dnsmasq.conf`, and logs the configuration status.

- #### Install Necessary Services

```bash
check_service_installed() {
    local service_to_check="$1"

    if systemctl list-unit-files --type=service | grep -q "^$service_to_check.service"; then
        echo "$service_to_check is installed" >> "$LOG_FILE_PATH"
    else
        echo "$service_to_check is being installed" >> "$LOG_FILE_PATH"

        sudo apt update
        sudo apt install -y "$service_to_check"

        if [ $? -eq 0 ]; then
            echo "$service_to_check has been installed successfully." >> "$LOG_FILE_PATH"
            configure_dnsmasq "$service_to_check"
        else
            echo "Failed to install $service_to_check. Please check and install it manually." >> "$LOG_FILE_PATH"
        fi
    fi
}
```

The `check_service_installed` function is responsible for checking if the necessary services are installed. If not, it attempts to install them using `apt` and then configures `dnsmasq` if the installation is successful. It logs the installation status and any errors encountered during the process.

- #### Copying Boot, Root Files, and Exporting Entries

```bash
create_mac() {
    local mac_address="$1"

    echo "**********Running script for $mac_address**********" >> "$LOG_FILE_PATH"

    configure_dnsmasq "dnsmasq"
    check_service_installed "nfs-kernel-server"
    check_service_installed "dnsmasq"

    echo "Creating $mac_address directories for tftp and nfs" >> "$LOG_FILE_PATH"
    sudo mkdir -p "/srv/tftp/$mac_address"
    sudo mkdir -p "/srv/nfs/$mac_address"

    echo "Copying rootfiles to /srv/nfs/$mac_address" >> "$LOG_FILE_PATH"
    sudo cp -a "/home/odroid/userfiles/"* "/srv/nfs/$mac_address"
    echo "Finished copying rootfiles" >> "$LOG_FILE_PATH"

    echo "Copying bootfiles to /srv/tftp/$mac_address" >> "$LOG_FILE_PATH"
    sudo cp -r "/home/odroid/bootfiles/"* "/srv/tftp/$mac_address"
    echo "Finished copying bootfiles" >> "$LOG_FILE_PATH"

    echo "Replacing contents of cmdline.txt" >> "$LOG_FILE_PATH"
    echo -e "console=serial0,115200 console=tty1 root=/dev/nfs nfsroot=192.168.XX.XX:/srv/nfs/$mac_address rw rootwait cgroup_memory=1 cgroup_enable=memory" | sudo tee "/srv/tftp/$mac_address/cmdline.txt" > /dev/null

    new_content="proc            /proc           proc    defaults          0       0\n\
    PARTUUID=4e639091-02  /               ext4    defaults,noatime  0       1\n\
    192.168.XX.XX:/srv/tftp/$mac_address /boot nfs defaults 0 0"

    echo "Replacing contents of fstab" >> "$LOG_FILE_PATH"
    echo -e "$new_content" | sudo tee "/srv/nfs/$mac_address/etc/fstab" > /dev/null

    echo "Adding nfs entry in /etc/exports" >> "$LOG_FILE_PATH"
    echo "/srv/nfs/$mac_address *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a "/etc/exports" > /dev/null

    echo "Adding tftp entry in /etc/exports" >> "$LOG_FILE_PATH"
    echo "/srv/tftp/$mac_address *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a "/etc/exports" > /dev/null

    echo "Running exportfs" >> "$LOG_FILE_PATH"
    sudo exportfs -r

    echo "**********Successfully completed execution for $mac_address**********" >> "$LOG_FILE_PATH"
}
```

This `create_mac` function is responsible for creating directories, copying boot files and user files, configuring the `cmdline.txt` file and `fstab` file, and adding the entries in the exports of the Odroid server.

### 3.2 Address List Management

The `addresslist.txt` file serves as a record of processed MAC addresses. Before executing the setup for a new MAC address, the script checks this list to ensure it hasn't already been configured. This prevents unnecessary duplication of efforts. Here's an example of how the `addresslist.txt` file might look:

```
00-11-22-33-44-55
aa-bb-cc-dd-ee-ff
```

### 3.3 Running the Script as a Daemon

To ensure continuous monitoring and execution of the `pxeService.sh` script, we can set it up as a daemon process using a systemd service unit file (`pxeService.service`). Here's how you can create and configure the service:

1. Create a new file named `pxeService.service` in the `/etc/systemd/system/` directory.
2. Add the following content to `pxeService.service`:

```ini
[Unit]
Description=PXE Service Daemon
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash /usr/bin/pxeService.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Save the file and exit the editor.
4. Reload systemd to read the new service unit:

```bash
sudo systemctl daemon-reload
```

5. Enable and start the `pxeService.service`:

```bash
sudo systemctl enable pxeService.service
sudo systemctl start pxeService.service
```

Now, the `pxeService.sh` script will run as a daemon, continuously monitoring and automating the netbooting process for new Raspberry Pi devices.

## 4. Conclusion

In this guide, we've covered the fundamentals of netbooting for Raspberry Pi devices using PXE boot, set up the necessary infrastructure components, and automated the booting process using bash scripting. By leveraging automation and creating a daemon service, you can significantly streamline the provisioning and maintenance of Raspberry Pi devices in your network.
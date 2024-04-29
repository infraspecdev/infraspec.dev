---
title: "Streamlining Raspberry Pi Deployment: A Guide to Automated Netbooting"
authorId: "rohit"
date: 2024-04-17
draft: false
featured: true
weight: 1
---

In this blog, we'll delve into automating the netbooting process using a bash script (`pxeService.sh`) and an address list (`addresslist.txt`) to enhance the deployment and management of Raspberry Pi devices. If you haven't already, you can catch up on the initial steps and concepts discussed [here](https://www.infraspec.dev/blog/rpi-netboot-deep-dive/), where we laid the groundwork for this automation project.

## Bash Script Overview

The `pxeService.sh` script is designed to automate the setup for each PXE client (Raspberry Pi device). You can take a look at the complete `pxeService.sh` script [here](https://github.com/infraspecdev/rpi-network-boot/blob/main/pxeScript.sh). Here's a breakdown of the script:

### Constants and Log Paths

In this code snippet, we define constants for the script, such as the UDP port to listen on `(PORT=69)` and the path for logging `(pxe_service_log_path="/var/log/pxeService.log")`. It's important to ensure that the pxeService.log file is created in the `/var/log` directory before running the script. This log file will store the script's output and any logged messages during its execution.

```bash
#!/bin/bash
PORT=69
pxe_service_log_path="/var/log/pxeService.log"
```

### Handling Error and Listening to Requests

One of the key components of the script is the use of `tcpdump`. This tool plays a critical role in real-time network monitoring. It allows the script to capture and analyze network traffic, specifically UDP requests on a specified port (`$PORT`). This capability is fundamental as it enables the script to detect and respond to incoming requests from PXE clients promptly.

```bash
# Function to handle errors
handle_error() {
	local line_number="$1"
	echo "An error occurred at line $line_number" >> "$pxe_service_log_path"
	exit 1
}

# Function to process UDP packets
process_udp_packets() {
	tcpdump -l -i any -e udp port "$PORT" | while read -r line; do
    	MAC=$(echo "$line" | awk '{print $6}' | tr ':' '-')
    	TIME=$(date +"%Y-%m-%d %H:%M:%S")

    	if grep -q "$MAC" /opt/addresslist.txt; then
        	echo "$MAC already exists" >> "$pxe_service_log_path"
    	else
        	echo "************Executing macscript.sh for $MAC***************" >> "$pxe_service_log_path"
        	echo "$MAC" >> /opt/addresslist.txt

        	FILE=$(echo "$line" | grep -o -P '(?<=RRQ ")[^"]+')
        	FILE=$(awk -F'/' '{print $NF}' <<< "$FILE")

        	if [ "$FILE" = "start4.elf" ]; then
            	echo "Time: $TIME, MAC address: $MAC, Requested file: $FILE" >> "$pxe_service_log_path"
            	configure_pxe_services "$MAC" &
            	echo "**********macscript execution finished for MAC $MAC**********" >> "$pxe_service_log_path"
        	else
            	echo "Not found" >> "$pxe_service_log_path"
        	fi
    	fi
	done
}

# Trap for handling errors
trap 'handle_error $LINENO' ERR

# Start processing UDP packets
process_udp_packets
```

### Configure dnsmasq.conf

Another vital aspect is configuring `dnsmasq` specifically for the TFTP (Trivial File Transfer Protocol) server functionality. In this context, `dnsmasq` serves as the TFTP server, which is essential for transferring boot files to PXE clients during the netbooting process. The `enable-tftp` option in the configuration enables TFTP support within `dnsmasq`, ensuring seamless file transfer operations. Additionally, the `tftp-root` parameter specifies the root directory for TFTP, providing a structured environment for storing and accessing boot files required by PXE clients.

```bash
# Function to configure dnsmasq service
configure_dnsmasq_service() {
	local service_name="$1"
	local dnsmasq_conf="/etc/dnsmasq.conf"

	if [ "$service_name" == "dnsmasq" ] && systemctl is-active --quiet "dnsmasq"; then
    	echo "Configuring $dnsmasq_conf..."

    	read -p "Enter the interface name (e.g., bond0): " interface_name

    	# Create or append to dnsmasq configuration
    	cat <<EOF | sudo tee -a "$dnsmasq_conf" > /dev/null
interface=$interface_name
no-hosts
enable-tftp
tftp-root=/srv/tftp
tftp-unique-root=mac
log-facility=/var/log/dnsmasq
port=5353
EOF

    	echo "Configuration has been added to $dnsmasq_conf" >> "$pxe_service_log_path"
	fi
}
```

### Install Necessary Services

The `ensure_service_installed function` checks if a specific service is already installed and active. If the service is not active, it attempts to install it using apt and then starts the service. If the installation and start are successful, it logs the outcome; otherwise, it logs a failure message.

```bash
# Function to ensure service is installed
ensure_service_installed() {
    local service_name="$1"

    if systemctl is-active --quiet "$service_name"; then
        echo "$service_name is already installed and active." >> "$pxe_service_log_path"
    else
        echo "Installing and starting $service_name..." >> "$pxe_service_log_path"

        sudo apt update
        sudo apt install -y "$service_name"

        if systemctl is-active --quiet "$service_name"; then
            echo "$service_name installed and started successfully." >> "$pxe_service_log_path"
            configure_dnsmasq_service "$service_name"
        else
            echo "Failed to install or start $service_name. Please check and install it manually." >> "$pxe_service_log_path"
        fi
    fi
}
```

### Copying Boot, Root Files and Exporting the Entries to Exports

The `configure_pxe_services` function is responsible for setting up the necessary directories, copying boot and root files, configuring cmdline.txt and fstab files, and adding entries to the exports of the Raspberry Pi server. It performs these actions to ensure the PXE services are properly configured for a specific MAC address, facilitating the netbooting process effectively.

```bash
# Function to configure PXE services
configure_pxe_services() {
	local mac_address="$1"
	local nfs_root="/srv/nfs/$mac_address"
	local tftp_root="/srv/tftp/$mac_address"
	local nfs_exports="/etc/exports"

	# Log start of script execution
	echo "**********Configuring PXE services for $mac_address**********" >> "$pxe_service_log_path"

	# Ensure required services are installed
	ensure_service_installed "nfs-kernel-server"
	ensure_service_installed "dnsmasq"

	# Create directories for TFTP and NFS
	echo "Creating directories for $mac_address in TFTP and NFS" >> "$pxe_service_log_path"
	sudo mkdir -p "$tftp_root" "$nfs_root"

	# Copy necessary files to NFS and TFTP directories
	echo "Copying root files to NFS directory" >> "$pxe_service_log_path"
	sudo cp -a "/home/pi/userfiles/"* "$nfs_root"
	echo "Finished copying root files" >> "$pxe_service_log_path"

	echo "Copying boot files to TFTP directory" >> "$pxe_service_log_path"
	sudo cp -r "/home/pi/bootfiles/"* "$tftp_root"
	echo "Finished copying boot files" >> "$pxe_service_log_path"

	# Configure cmdline.txt for boot parameters
	echo "Configuring boot parameters in cmdline.txt" >> "$pxe_service_log_path"
	echo -e "console=serial0,115200 console=tty1 root=/dev/nfs nfsroot=192.168.XX.XX:$nfs_root rw rootwait" | sudo tee "$tftp_root/cmdline.txt" > /dev/null

	# Update fstab with NFS mount entry
	local new_fstab_content="proc        	/proc       	proc	defaults      	0   	0\n\
	PARTUUID=4e639091-02  /           	ext4	defaults,noatime  0   	1\n\
	192.168.XX.XX:$tftp_root /boot nfs defaults 0 0"

	echo "Updating fstab with NFS mount entry" >> "$pxe_service_log_path"
	echo -e "$new_fstab_content" | sudo tee "$nfs_root/etc/fstab" > /dev/null

	# Add NFS and TFTP entries to exports file
	echo "Adding NFS export in $nfs_exports" >> "$pxe_service_log_path"
	echo "$nfs_root *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a "$nfs_exports" > /dev/null

	echo "Adding TFTP export in $nfs_exports" >> "$pxe_service_log_path"
	echo "$tftp_root *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a "$nfs_exports" > /dev/null

	# Reload NFS exports
	echo "Reloading NFS exports" >> "$pxe_service_log_path"
	sudo exportfs -r

	# Log completion of script execution
	echo "**********Successfully configured PXE services for $mac_address**********" >> "$pxe_service_log_path"
}
```

## Address List Management

The `addresslist.txt` file serves as a record of processed MAC addresses. Before executing the setup for a new MAC address, the script checks this list to ensure it hasn't already been configured. This prevents unnecessary duplication of efforts. Make sure to create `addresslist.txt` in `/opt` directory. Here's an example of how the `addresslist.txt` file might look:

```
00-11-22-33-44-55
aa-bb-cc-dd-ee-ff
```

## Running the Script as a Daemon

To ensure continuous monitoring and execution of the `pxeService.sh` script, we can set it up as a daemon process using a systemd service unit file (`pxeService.service`). Here's how you can create and configure the service:

1. Copy the `pxeService.sh` file to `/usr/bin` directory.
2. Create a new file named `pxeService.service` in the `/etc/systemd/system/` directory.
3. Add the following content to `pxeService.service`:

```bash
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

Save the file and exit the editor, then reload systemd to read the new service unit:

```bash
sudo systemctl daemon-reload
```

Enable and start the `pxeService.service`

```bash
sudo systemctl enable pxeService.service
sudo systemctl start pxeService.service
```

Now, the `pxeService.sh` script will run as a daemon, continuously monitoring and automating the netbooting process for new Raspberry Pi devices.

## Conclusion

In this guide, we've automated the booting process using bash scripting. By leveraging automation and creating a daemon service, you can significantly streamline the provisioning and maintenance of Raspberry Pi devices in your network.
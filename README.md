For resource and budget optimization purposes, it can be very useful to have a way of keeping control of deployments in a cloud tenant by generating, via APIs, a report of the number of resources by category and with dynamic date filtering.



To begin with, in order to isolate the script execution environment, we'll create a python virtual environment for it and install the dependencies required for its execution using pip.

#### Creating a python virtualenv

Install the latest version of python (3.x)

```bash
dnf install python3
```

Create the venv

```bash
#Create the virtual env
python3 -m venv /my_env_path/

#Use virtual env
. /my_env_path/bin/activate
```

## Installation of dependencies with pip

## Install pip

```bash
pip install -U pip
```

## Installing oci-cli command

```bash
pip install oci-cli
```

## Configure oci-cli

After installation, configure authentication using the command below

```bash
oci setup config
```

This will guide you through configuring authentication information, including adding your API key, API secret and other necessary details.

- **Configure Authentication**: Configure authentication using this will guide you through configuring authentication information, including adding your API key, API secret, and other details.
- **Region configuration**: Configure the region using or by modifying the OCI configuration file (`~/.oci/config`). Select the appropriate region for your Oracle Cloud Infrastructure.
- **Installation check**: Check that the OCI CLI is correctly installed by running :

```bash
oci --version
```

## Trying oci-cli

Once configured, you can use the OCI CLI to perform actions such as listing instances, volumes, networks, etc. Use commands like `oci compute instance list` to list instances. Use commands like `oci compute instance list` to list instances.( Be sure to adjust `<compartment-id>` with the ID of the appropriate compartment where your instances are located).

```bash
oci compute instance list --compartment-id <compartment-id>
```

## Use the script

Once the basic environment has been set up and is up and running, all we have to do is install our script on the server and run it.

List of items retrieved by

- compartment
- instances
- vcns
- block storage attached
- block storage unattached
- boot volumes
- boot volume backups
- volume group
- volume group backup
- volume backups
- bucket
- autonomous dbs
- pluggable dbs
- systems dbs
- simple dbs


Once the script has been copied to the server, simply execute it, setting the number of days to be applied as the delta between the creation date of each resource and the script execution date.

```bash
python3 my_script.py 1000
```

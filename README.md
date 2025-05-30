# Analysis Facility metrics collector

AF Metrics Collector collects various metrics about user jobs from kubernetes,
batch systems and send the collected metrics as json documents to an https endpoint.

## Installation

### Prerequisites:

- Have installed `python3` and `pip3` system packages

- Install some python dependencies for afmetrics_collector: `pip3 install -U setuptools setuptools_scm wheel importlib_metadata`

- Create a directory for the log files: `mkdir /var/log/afmetrics`

### Install afmetrics_collector:

Clone the git repo onto your server

Navigate to the project directory

(optional) Make changes to setup.cfg

Build with python3: `python3 setup.py bdist_wheel`

Install with pip3: `pip3 install dist/afmetrics_collector-0.0*.whl`

## Uninstallation

`pip3 uninstall afmetrics-collector`

## Installation (RPM)

### Prerequisites:

- Have installed `python3-kubernetes` system package

- Create a directory for the log files: `mkdir /var/log/afmetrics`

### Install afmetrics_collector rpm package:

Clone the git repo onto your server

Navigate to the project directory

(optional) Make changes to setup.cfg

Build with python3: `python3 setup.py bdist_rpm`

Install with yum or dnf: `dnf install dist/afmetrics_collector-0.0*.rpm`


## Sending documents

All the documents should be __POST__ to <https://af.atlas-ml.org>.

## Documents

Each document has to have a token field. To get a token for your AF, please contact Ilija Vukotic.
All documents get timestamped on the receiving end so no need to send them. Here an example of each metric.


### Batch queue status

this is obtained by parsing output of __condor_q__ command.

```json
{  
    "kind": "condorqueue",
    "cluster": "UC-AF",
    "queue": "all",
    "idle": 1995,
    "running": 1022,
    "held": 3,
    "allocated_cores": 966,
    "allocated_mem": 4145152
}
```

### SSH users

this is obtained by parsing output of __who__ command.

```json
{   
    "kind": "ssh",
    "ssh_user_count": 4,
    "cluster": "UC-AF",
    "login_node": "login01.af.uchicago.edu",
    "users": [
      "brosser",
      "mhank",
      "milaivanovska",
      "rjacobse"
    ]
}
```

### Condor users

obtained by parsing output of __condor_q__ command.

```json
{   
    "kind": "condorjob",
    "cluster": "UC-AF",
    "users": "brosser",
    "state": "finished",
    "Id": "174100.63",
    "Runtime": 177
}
```

### Jupyter users

```json
{   
    "kind": "jupyter-ml",
    "cluster": "UC-AF",
    "jupyter_user_count": 4,
    "users": [
      "agolub",
      "gwatts",
      "hanhiller",
      "petya"
    ]
}
```

### Disk

One document for each disk reporting used, total and free bytes as seen from __/proc/diskstats__

```json
{   
    "kind": "DISK",    
    "cluster": "UC-AF",
    "used": 92355981312,
    "total": 1883690205184,
    "free": 1695620259840,
    "login_node": "login02.af.uchicago.edu",
    "utilization": 0.04902928361459448,
    "mount": "/scratch"
}
```

### CPU

Just a one minute load average as reported by __os.getloadavg()__.

```json
{       
    "kind": "CPU",
    "cluster": "UC-AF",
    "login_node": "login02.af.uchicago.edu",
    "load": 0.01
}
```

### Network

Differential of bytes_sent, bytes_recv and the time interval, as reported by __psutil.net_io_counters()__.

```json
{       
    "kind": "NETWORK",
    "cluster": "UC-AF",
    "login_node": "login02.af.uchicago.edu",
    "network": {
      "interval": 300.064,
      "sent": 6606414,
      "received": 11383868
    }
}
```

### Memory

Host total and available memory as reported by __psutil.virtual_memory()__. In bytes.

```json
{   
    "kind": "MEM",
    "cluster": "UC-AF",
    "login_node": "login02.af.uchicago.edu",
    "available": 265041854464,
    "total": 269903060992
}
```

## Usage and examples

**In the following replace all instances of `<token>` with your actual token, likewise for mentions of `<cluster>`, `<domain>`, `<salt>`, and so on. These are placeholders for your real values**

A typical full installation will collect ssh, batch (condor), jupyter, and host metrics and the command to run may look something like this:

`afmetrics_collector -v -sjb --host -t "<token>" -c "<cluster>"`

The associated cron job to run this every 5 minutes (the default and recommended interval) may look like this:

`*/5 * * * * root (KUBECONFIG=/etc/kubernetes/admin.conf /usr/local/bin/afmetrics_collector -v -sjb --host -t "<token>" -c "<cluster>") >> /var/log/afmetrics/afmetrics.log 2>&1`

## Advanced Usage

### Batch queue status reporting

By default no batch queue status is reported. To add queue status reporting, add the queue in this format "queuename:condor query contraint expression". For example the following command will collect status of two queues, the all inclusive queue and the short queue which can be queried with queue=="short" constraint.

`afmetrics_collector -vv -b -t <token> -c "<cluster>" -q all: -q 'short:queue=="short"'`

### SSH history

**Only usable for systems with a version of `last` command that include `-s` option**

In addition to ssh users currently logged in, adding the `-S` flag will include users who logged in within the last 5 minutes as well (to account for a possible edge case which includes users that log in and out really fast)

`afmetrics_collector -vv -sjb -S --host -t <token> -c "<cluster>"`

### Group Filtering

Useful on systems that may serve as login nodes for many users unaffiliated with what you are interested in, add the `-g` or `--group` flag to filter for a specific group

For example, if you are only interested in ssh logins, jupyter, and batch jobs of users in group 'atlas', the command may look like the following:

`afmetrics_collector -vv -sjb --host -t <token> -c "<cluster>" -g "atlas"`

### Debugging

For debugging, you can opt to output everything to a local file instead of sending it to the logstash server with the `-d` flag:

`afmetrics_collector -d -vv -sjb --host -t <token> -c "<cluster>"`  
This will output .json files in your current directory, and very verbose (`-vv`) logs to stdout.  
I would recommend to pipe the output to a file `afmetrics.log` by appending `>> afmetrics.log 2>&1` to the command so that the general output can be inspected as well as the json.  
A **token** is not necessary for debugging, so you can use `-d` before you have one

### Data Obfuscation and security

For sites that wish to share usage metrics, but not info such as usernames and hostnames, data obfuscation flags `-o`, `-O`, and `-z` have been added:

> `-o` : user name obfuscation
>
> `-O` : host name obfuscation, followed by a string domain name, ex.: `-O 'bnl.gov'`
>
> `-z` : (optional) salt to make user obfuscation more secure, ex.: `-o -z '5tKC%>f&%#hg'`

Afmetrics_collector can be run as users other than **root**. If you wish to do this, make sure the ownership/permissions of the `/var/log/afmetrics` directory is such that the desired user can write to it

A full example using all of the obfuscation and a local debug running as user 'nobody', along with a group filter might look something like this:

`su -s /bin/bash -c '(/usr/local/bin/afmetrics_collector -d -vv -sbj --host -t "<token>" -o -O "<domain>" -c "<cluster>" -z "<salt>" -g "<group>") 2>&1' nobody`

The associated cron `/etc/cron.d/afmetrics.cron` running all of the above in non-debug mode may looks like this:

```
### Afmetrics Collector ###
SHELL=/bin/bash
HOME=/var/log/afmetrics
*/5 * * * * nobody (/usr/local/bin/afmetrics_collector -vv -sbj --host  -t "<token>" -o -O "<domain>" -c "<cluster>" -z "<salt>" -g "<group>") >> /var/log/afmetrics/afmetrics.log 2>&1
```

#### How it works: 

**Username obfuscation** simply MD5 hashes username and truncates to the last 8 characters. Salt can be added to the username hash to strengthen against rainbow table attacks. **If salt is used, make sure to use the same salt value across all your login nodes, otherwise the same user will be counted as a unique user if they log in on many nodes.**

**Hostname obfuscation** is very basic so may need to be modified to suit your facility. It simply takes your hostname, strips off everything except the numbers, and prepends **'atlas'** and appends **your provided domain name string**.  
For example if your host is called `condor123.example.edu` and you call the hostname obfuscation flag with `-O "bnl.gov"` you will get `atlas123.bnl.gov` as your obfuscated domain name.  
Provided the numbers from all your login hosts are different you should end up with no collisions. Modify in `src/afmetrics_collector/skeleton.py` to suit your needs

Note
====

This project has been set up using PyScaffold 4.2.1. For details and usage
information on PyScaffold see <https://pyscaffold.org/>.

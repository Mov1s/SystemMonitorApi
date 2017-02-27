from flask import Blueprint, jsonify
from ago import human
from datetime import datetime
import re
from apihelper import *

api = Blueprint('api', __name__)

@api.route('/system/network/internet')
@support_jsonp
@handle_errors
def getInternetInfo():
    """Return the current internet speeds up/down."""
    out = run_from_shell('speedtest')
    down_match = re.search('Download: ([\d\.]+).*', out)
    up_match = re.search('Upload: ([\d\.]+).*', out)
    return jsonify({
        "up" : up_match.group(1),
        "down" : down_match.group(1) })


@api.route('/system/network/current')
@support_jsonp
@handle_errors
def getCurrentNetworkInfo():
    """Return the current system up/down for NIC enp1s0."""
    out = run_from_shell("sar", "-n", "DEV", "2", "1")
    match = re.search('[\d:]+.*enp1s0\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*).*', out)
    return jsonify({
        "up" : "%.2f" % (float(match.group(4)) / 1000),
        "down" : "%.2f" % (float(match.group(3)) / 1000) })


@api.route('/system/info')
@support_jsonp
@handle_errors
def getSystemInfo():
    """Return the last time pacman -Syu was run."""
    out = run_from_shell('cat', '/var/log/pacman.log')
    lastdate = re.findall('\[([\d\-: ]+)\].*-Syu.*', out)[-1]
    time = datetime.strptime(lastdate, '%Y-%m-%d %H:%M')
    return jsonify({
        "last_update" : human(time, precision=1) })


@api.route('/system/storage')
@support_jsonp
@handle_errors
def getStorageInfo():
    """Return information about the array md127."""

    #Get disk usage
    out = run_from_shell('df', '-BG')
    match = re.search('/dev/md127\s+([\d\.]+)G\s+([\d\.]+)G.*', out)
    json = {
        "total" : "%.2f" % (float(match.group(1)) / 1024),
        "used" : "%.2f" % (float(match.group(2)) / 1024) }

    #Get array health
    out = run_from_shell('cat', '/proc/mdstat')
    match = re.search('.*\[U+\].*', out)
    json["array_healthy"] = match != None
    return jsonify(json)


@api.route('/system/cpu')
@support_jsonp
@handle_errors
def getCpuInfo():
    """Return information about the CPU and RAM."""

    #Get CPU temp
    out = run_from_shell("sensors")
    match = re.search('.*CPUTIN:\s+\+([\d\.]*).*', out)
    json = { "cpu_temp" : match.group(1) }

    #Get CPU usage
    out = run_from_shell("mpstat", "2", "1")
    match = re.search('.*all\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)\s+([\d\.]*)', out)
    json["cpu_usage"] = "%.2f" % (100 - float(match.group(10)))

    #Get RAM usage
    out = run_from_shell("free", "-m")
    match = re.search('.*Mem:\s+([\d\.]*)\s+([\d\.]*).*', out)
    json["ram_total"] = "%.2f" % (float(match.group(1)) / 1024)
    json["ram_used"] = "%.2f" % (float(match.group(2)) / 1024)
    return jsonify(json)

import argparse
from collections import defaultdict
from prettytable import PrettyTable
import json
import sys
import subprocess


def get_status():
    output = subprocess.check_output(['juju', 'status', '--format', 'json'])

    return json.loads(output)


def setup_options(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--machines', dest="machines", action='store_true')
    parser.add_argument('--errors', dest="errors", action='store_true')
    parser.add_argument('--services', dest="services", action='store_true')
    parser.add_argument('--sort-by', dest="sort_by", default=None)

    return parser.parse_args(argv)


def pprint_errors(st):
    pass


def pprint_machines(st, sort_by=None):
    x = PrettyTable(["id", 'agent', 'dns-name'])
    x.align['agent'] = x.align['dns-name'] = 'l'
    for mkey in st["machines"]:
        r = st['machines'][mkey]
        x.add_row([mkey, r['agent-state'], r['dns-name']])

        for ckey in r.get('containers', []):
            c = r['containers'][ckey]
            x.add_row([ckey, c['agent-state'], c['dns-name']])

    if sort_by:
        print x.get_string(sortby=sort_by)
    else:
        print x


def pprint_services(st, sort_by=None):
    x = PrettyTable(['name (units)', 'agent-state'])
    x.align['name (units)'] = 'l'
    STATES = defaultdict(lambda: 0)
    STATES["started"] = 10

    for sname in st['services']:
        r = st['services'][sname]

        if 'units' in r:
            num_units = len(r['units'].keys())
        else:
            num_units = 'N/A'

        worst_state = "started"
        problematic_units = []
        for uname in r.get('units', []):
            if STATES[r['units'][uname]['agent-state']] < STATES[worst_state]:
                worst_state = r['units'][uname]['agent-state']
                problematic_units.append(uname.split('/')[-1])

        x.add_row(['%s (%s)' % (sname, num_units),
                   '%s (%s)' % (worst_state, ", ".join(problematic_units))])

    if sort_by:
        print x.get_string(sortby=sort_by)
    else:
        print x


def main(argv=None):
    opts = setup_options(argv)

    st = get_status()

    if opts.errors:
        pprint_errors(st)

    if opts.machines:
        pprint_machines(st, opts.sort_by)

    if opts.services:
        pprint_services(st, opts.sort_by)


if __name__ == "__main__":
    main()

import json

with open('out.json') as f:
    mapping = json.load(f)

devices = {}
suffixes = {}

def simplify_reverse_deps(repo, device):
    # repo['branch'] = cm-14.1 or cm-14.1-caf or cm-14.1-sony
    if 'branch' in repo and repo['branch'].count('-') > 1: # get suffix
        if repo['repo'] not in suffixes:
            suffixes[repo['repo']] = {}
        suffixes[repo['repo']][device] = '-' + repo['branch'].split('-', 2)[2]

    if repo['repo'] not in mapping or len(mapping[repo['repo']]) == 0:
        return [repo['repo']]
    res = []
    for i in mapping[repo['repo']]:
        res += (simplify_reverse_deps(i, device))
    res.append(repo['repo'])
    return res

for repo in mapping:
    if 'device' in repo and 'common' not in repo:
        codename = repo.split('_', maxsplit=3)[-1]
        if codename in devices:
            print("warning: dupe: %s"%codename)

        devices[codename] = sorted(list(set(simplify_reverse_deps({'repo': repo}, codename))))

with open('devices.json', 'w') as f:
    out = {'devices': devices, 'suffixes': suffixes}
    out = devices
    json.dump(out, f, indent=4, sort_keys=True)

import json

# Define device repos that have repos that depend on them,
# otherwise the script will remove these on the assumption
# they are common repos
COMMON_DEVICE = [
    'android_device_asus_flo',
    'android_device_asus_grouper',
    'android_device_google_marlin',
    'android_device_samsung_espressowifi',
    'android_device_samsung_n1awifi',
    'android_device_samsung_t0lte',
]

with open('out.json') as f:
    mapping = json.load(f)

kernels = {}

reverse_deps = {}

for device in mapping:
    deps = mapping[device]
    if device not in reverse_deps:
        reverse_deps[device] = []
    for repo in deps:
        if repo['repo'] not in reverse_deps:
            reverse_deps[repo['repo']] = []
        reverse_deps[repo['repo']].append(device)

def simplify_reverse_deps(repo):
    if len(reverse_deps[repo]) == 0 and '-common' not in repo:
        return {repo,}
    res = set()
    for i in reverse_deps[repo]:
        res.update(simplify_reverse_deps(i))
    if repo in COMMON_DEVICE:
        res.add(repo)
    return res

for repo in reverse_deps:
    if 'kernel' in repo:
        kernels[repo] = sorted(list(simplify_reverse_deps(repo)))

with open('kernels.json', 'w') as f:
    json.dump(kernels, f, indent=4, sort_keys=True)

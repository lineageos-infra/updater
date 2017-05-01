import json

COMMON_DEVICE = [
    'android_device_asus_flo',
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
    if len(reverse_deps[repo]) == 0:
        return {repo,}
    res = set()
    for i in reverse_deps[repo]:
        res.update(simplify_reverse_deps(i))
    if repo in COMMON_DEVICE:
        res.add(repo)
    return res

for repo in reverse_deps:
    if 'kernel' in repo:
        kernels[repo] = list(simplify_reverse_deps(repo))

with open('kernels.json', 'w') as f:
    json.dump(kernels, f, indent=4)

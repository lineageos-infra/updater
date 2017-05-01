import concurrent.futures
import github
import json
import traceback

from github import Github
from base64 import b64decode

with open('token') as f:
    g = Github(f.readline().strip(), per_page=200)


print(g.rate_limiting_resettime)

org = g.get_organization('LineageOS')

# supported branches, newest to oldest
CUR_BRANCHES = ['cm-14.1', 'cm-13.0']

def get_cm_dependencies(repo):
    branch = None
    for b in CUR_BRANCHES:
        try:
            branch = repo.get_branch(b)
            break
        except github.GithubException:
            continue

    if branch is None:
        return None

    sha = branch.commit.sha
    try:
        tree = repo.get_git_tree(sha)
    except github.GithubException:
        return None
    blob_sha = None
    for el in tree.tree:
        if el.path == 'cm.dependencies' or el.path == 'lineage.dependencies':
            blob_sha = el.sha
            break

    if blob_sha is None:
        return [[], set()]

    blob = repo.get_git_blob(blob_sha)

    deps = b64decode(blob.content)

    cmdeps = json.loads(deps.decode('utf-8'))

    mydeps = []
    non_device_repos = set()
    for el in cmdeps:
        if '_device_' not in el['repository']:
            non_device_repos.add(el['repository'])
        depbranch = el.get('branch', branch.name)
        mydeps.append({'repo': el['repository'], 'branch': depbranch})

    return [mydeps, non_device_repos]

futures = {}
n = 1

dependencies = {}
other_repos = set()


with concurrent.futures.ThreadPoolExecutor() as executor:
    for repo in g.get_organization('LineageOS').get_repos():
        if '_device_' not in repo.name:
            continue
        print(n, repo.name)
        n += 1
        futures[executor.submit(get_cm_dependencies, repo)] = repo.name
    for future in concurrent.futures.as_completed(futures):
        name = futures[future]
        try:
            data = future.result()
            if data is None:
                continue
            dependencies[name] = data[0]
            other_repos.update(data[1])
            print(name, "=>", data[0])
        except Exception as e:
            print('%r generated an exception: %s'%(name, e))
            traceback.print_exc()
            continue
    futures = {}

    print(other_repos)
    for name in other_repos:
        print(name)
        try:
            repo = org.get_repo(name)
            futures[executor.submit(get_cm_dependencies, repo)] = name
        except Exception:
            continue

    other_repos = {}
    for future in concurrent.futures.as_completed(futures):
        name = futures[future]
        try:
            data = future.result()
            if data is None:
                continue
            dependencies[name] = data[0]
            for el in data[1]:
                if el in dependencies:
                    continue
                other_repos.update(data[1])
            print(name, "=>", data[0])
        except Exception as e:
            print('%r generated an exception: %s'%(name, e))
            traceback.print_exc()
            continue
    futures = {}


print(other_repos)
#for name in other_repos:
#    repo = org.get_repo(name)
#    dependencies[name] = get_cm_dependencies(repo)

with open('out.json', 'w') as f:
    json.dump(dependencies, f, indent=4)

1. Use Python 3.2 or higher
2. `pip install -r requirements.txt`
3. grab a new token from [here](https://github.com/settings/tokens) - no scopes needed, just a name. Put it in `token`
4. run `python app.py` to generate the full lineage.dependencies mapping
5. run `python device2kernel.py` to generate kernel -> devices mapping
6. run `python devices.py` to generate device -> dependency mapping (like ../device_deps.json)

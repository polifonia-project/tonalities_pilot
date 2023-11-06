import glob
import os
import yaml

# CONSTANTS & CONFIG

with open('conf.yaml') as f:
    conf = yaml.load(f, Loader=yaml.loader.SafeLoader)

# LIST SCORES

mei_files = glob.glob('../../scores/**/*.mei', recursive=True)

os.remove('scores-url-list.txt')
with open('scores-url-list.txt', 'w') as flist:
    for f in mei_files:
        url = f \
            .replace('../../scores/', conf['polifonia']['tonalities']['scores']['base_url']) \
            .replace(' ', '%20')
        flist.write(url + "\n")

import os
import shutil
import subprocess
import sys

import oyaml as yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from kfcicli.main import *
from kfcicli.utils import setup_logging
import json

logger = setup_logging(log_level="INFO", logger_name=__name__)

with open("./credentials.json", "r") as fid:
    credentials = GitCredentials(**json.loads(fid.read()))

tmp_folder = f"/home/ubuntu/tmp/kfcicli/charm_repos"
logger.info(f"Using temporary directory: {tmp_folder}")

filename=Path("../../presets/kubeflow-multi-charm.yaml")

client = KubeflowCI.read(
    filename=filename,
    base_path=Path(f"{tmp_folder}"),
    credentials=credentials
)

CURRENT_FOLDER = Path(__file__).parent

def call_script(script: Path, path: Path) -> bool:

    shutil.copy(script, path / script.name)

    try:
        subprocess.check_call(["/bin/bash", script.name],
                              cwd=path,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        os.remove(path / script.name)


def process_repo(repo: Client, charms: list[LocalCharmRepo], dry_run: bool):
    success = call_script(CURRENT_FOLDER / "replace-cache.sh", repo.base_path)
            
    if repo.is_dirty():
        repo.update_branch(
            commit_msg=f"Updating GitHub action file", directory=".",
            push=not dry_run, force=True
        )

with open("body.md", "r") as f:
    pr_body = f.read()

client.canon_run(
    wrapper_func=process_repo,
    branch_name="kf-7561-enable-cache",
    title="chore: Re-enable usage of cache while bulding charms",
    body=pr_body,
    dry_run=False
)

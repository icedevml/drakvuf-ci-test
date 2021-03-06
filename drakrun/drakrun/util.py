import base64
import os
import sys
import subprocess

from karton2 import Config


def patch_config(cfg):
    try:
        access_key = cfg.config['minio']['access_key']
        secret_key = cfg.config['minio']['secret_key']
    except KeyError:
        sys.stderr.write('WARNING! Misconfiguration: section [minio] of config.ini doesn\'t contain access_key or secret_key.\n')
        return cfg

    if not access_key and not secret_key:
        if not os.path.exists('/etc/drakcore/minio.env'):
            raise RuntimeError('ERROR! MinIO access credentials are not configured (and can not be auto-detected), unable to start.\n')

        with open('/etc/drakcore/minio.env', 'r') as f:
            minio_cfg = [line.strip().split('=', 1) for line in f if line.strip() and '=' in line]
            minio_cfg = {k: v for k, v in minio_cfg}

        try:
            cfg.config['minio']['access_key'] = minio_cfg['MINIO_ACCESS_KEY']
            cfg.config['minio']['secret_key'] = minio_cfg['MINIO_SECRET_KEY']
            cfg.minio_config = dict(cfg.config.items("minio"))
        except KeyError:
            sys.stderr.write('WARNING! Misconfiguration: minio.env doesn\'t contain MINIO_ACCESS_KEY or MINIO_SECRET_KEY.\n')

    return cfg


def get_domid_from_instance_id(instance_id: str) -> int:
    output = subprocess.check_output(["xl", "domid", f"vm-{instance_id}"])
    return int(output.decode('utf-8').strip())

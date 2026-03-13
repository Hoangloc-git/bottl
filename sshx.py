import subprocess

cmd = "curl -sSf https://sshx.io/get | sh -s run"

subprocess.run(
    cmd,
    shell=True,
    check=True
)

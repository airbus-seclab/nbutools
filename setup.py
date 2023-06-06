from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = [l for l in f.readlines() if l]

setup(
    name="nbutools",
    version="0.1",
    description="Utils for auditing a NetBackup infrastructure written in python",
    long_description=long_description,
    author="AirbusSeclab",
    packages=["utils", "GetConfigInfos", "PreAuthCartography", "ListUsersInfoFromDB"],
    scripts=["bin/nbuscan.py", "bin/nbumap.py", "bin/nbudbdump.py"],
    install_requires=requirements,
)

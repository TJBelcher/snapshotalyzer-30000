from setuptools import setup

setup(
    name='snapshota1yzer-30000',
    version='0.1',
    author="T Belcher",
    author_email="tbelcher@verizon.net",
    summary="SnapshotAlyzer 30000 is a tool to manage AWS EC2 snapshots",
    license="GPLv3+",
    packages=['shotty'],
    url="https://github.com/TJBelcher/snapshotalyzer-30000",
    install_requres=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    '''
        ,
)

import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    """Shotty manages ec2, volumes and snapshots"""

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            tags2 = { t['Key']:  t['Value'] for t in v.tags or [] }
            print(', '.join((
                v.id,
                i.id,
                v.volume_type,
                v.encrypted and "Encrypted" or "Unencrypted", #boolean
                str(v.size) + " GiB",
                v.state,
                tags2.get('Project', '<no project>'))))
    return

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', "list_all", default=False, is_flag=True,
    help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project, list_all):
    "List EC2 volume snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                tags3 = { t['Key']:  t['Value'] for t in s.tags or [] }
                print(', '.join((
                    s.id,
                    s.volume_id,
                    s.encrypted and "Encrypted" or "Unencrypted", #boolean
                    s.owner_id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c"),
                    tags3.get('Project', '<no project>'))))

                if not list_all:
                    if s.state == 'completed': break #this prints only 1 per volume

    return


@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot',
    help="Create snapshots of all volumes")
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)
    icount = 0
    vcount = 0
    for i in instances:
        print("Stopping instance {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()
        icount += 1
        for v in i.volumes.all():
            print("Creating snapshot for {0}".format(v.id))
            v.create_snapshot(Description="Created by Snapshotalyzer 30000")
            vcount += 1
        print("Starting {0}...".format(i.id))
        i.start()  #do not have to wait for completion of snapshot to restart
        print("Waiting for {0} to start...".format(i.id))
        i.wait_until_running() #wait for each machine to come up before next

    print("Job is complete!")
    print("Snapshots taken for {0} volumes across {1} instances".format(str(vcount), str(icount)))

    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']:  t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>'))))
    return

@instances.command('stop')
@click.option('--project', default=None,
    help='Only instances for the project')
def stop_instances(project):
    "Stop EC2 instances for project or all if no project provided"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}....".format (i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None,
    help='Only instances for the project')
def start_instances(project):
    "Start EC2 instances for project or all if no project provided"

    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}....".format (i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not start {0}. ".format(i.id) + str(e))
            continue

    return

if __name__ == '__main__':
    cli()

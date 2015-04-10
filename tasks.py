import os
from invoke import task, run

def _get_name(path):
    return os.path.splitext(os.path.split(path)[1])[0]

@task
def requirements(upgrade=True):
    cmd = 'pip install -r requirements.txt'
    if upgrade:
        cmd += ' --upgrade'
    run(cmd)

@task
def apify(file_name, sqla_string, primary_name='id', insert=True):
    cmd_csv = 'in2csv {0}'.format(file_name)
    cmd_sql = 'csvsql --db {0} --primary {1} --tables {2}'.format(
        sqla_string,
        primary_name,
        _get_name(file_name),
    )
    if insert:
        cmd_sql += ' --insert'
    cmd = '{0} | {1}'.format(cmd_csv, cmd_sql)
    run(cmd)

@task
def serve(sqla_string, port=5000, debug=False):
    from sandman import app
    from sandman.model import activate
    import utils
    app.json_encoder = utils.APIJSONEncoder
    app.config['SQLALCHEMY_DATABASE_URI'] = sqla_string
    activate()
    app.run(port=port, debug=debug)

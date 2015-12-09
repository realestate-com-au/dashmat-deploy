Python Dashing
==============

This is a dashboard framework written in Python.

More documentation and tests are coming. First we convert it to react.

To bootstrap deployment and viewer roles

	# For each environment
	# Modify deploy/roles/{deploy.yaml,viewer.yaml,accounts.yaml} and replace <placeholders>
	$ ./deploy/roles/syncr <env> sync --dry-run
	$ ./deploy/roles/syncr <env> sync

To deploy:

	# Modify <placeholders> in deploy/aws/bespin.yml
	# Modify <placeholders> in python_dashing/config.yml
	# Modify <placeholder> in deploy/files/ansible/roles/nginx/templates/app.conf
	# Modify required_version in run.sh to be the version of python-dashing you wish to use
	# Modify <officeip> in deploy/aws/app.json
	# Modify <placeholder> in deploy/files/ansible/roles/python-dashing/templates/python-dashing.init

	$ ENV=devprod BUILD_NUMBER=9001 ./deploy/bamboo/make_artifact.sh
	$ ENV=devprod BUILD_NUMBER=9001 ./deploy/bamboo/deploy.sh


Roles
=====

These are the AWS roles we use for deploying

To sync with Amazon:

#. Make your changes to ``deploy/roles/<env>/deploy.yaml``

#. Sync staging:

.. code-block:: ShellSession

    $ ./deploy/roles/syncr stg sync --dry-run
    $ ./deploy/roles/syncr stg sync

#. Sync production:

.. code-block:: ShellSession

    $ ./deploy/roles/syncr prod sync --dry-run
    $ ./deploy/roles/syncr prod sync


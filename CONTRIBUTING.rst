.. This file is part of EUDAT B2Share.
   Copyright (C) 2016, CERN.

   B2Share is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 2 of the
   License, or (at your option) any later version.

   B2Share is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with B2Share; if not, write to the Free Software Foundation, Inc.,
   59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

   In applying this license, CERN does not
   waive the privileges and immunities granted to it by virtue of its status
   as an Intergovernmental Organization or submit itself to any jurisdiction.

============
Contributing
============

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/EUDAT-B2SHARE/b2share/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

B2Share could always use more documentation, whether as part of the
official B2Share docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/EUDAT-B2SHARE/b2share/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

Get Started!
------------

Ready to contribute? Here's how to set up `b2share` for local development.

1. Fork the `B2Share` repo on GitHub.
2. Clone your fork locally:

   .. code-block:: console

      $ git clone git@github.com:your_name_here/b2share.git

3. Install your local copy into a virtualenv.

   .. code-block:: console

      $ mkvirtualenv b2share
      $ cd b2share/
      $ pip install -e .[all]

4. Create a branch for local development:

   .. code-block:: console

      $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass tests:

   .. code-block:: console

      $ ./run-tests.sh

   The tests will provide you with test coverage and also check PEP8
   (code style), PEP257 (documentation), flake8 as well as build the Sphinx
   documentation and run doctests.

6. Commit your changes and push your branch to GitHub:

   .. code-block:: console

      $ git add .
      $ git commit -s -m "Your detailed description of your changes."
      $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Branch switching
~~~~~~~~~~~~~~~~

B2SHARE runs Python, which creates intermediate ``.pyc`` files. When
switching branch uncommitted (ignored) files can remain. Before running
the server, make sure to remove all ``.pyc`` files first.

*NOTE: don't forget to rsync your files to the VM, if you're running
Vagrant*

.. code:: bash

    cd /path/to/b2share
    find . -name "*.pyc" -exec rm -rf {} \;
    git branch `<targetbranch#issueno-some-desc>`

Syncing upstream
~~~~~~~~~~~~~~~~

Once you have your fork, and local branch, keeping your branches updated
is important. After numerous merges your branches can become outdated,
and pull-requests are no longer able to automatically-merge, so fetch
upstream regularly!

*NOTE: before merging upstream, make sure you're on the correct branch
locally!*

**Add remote upstream**

Allows git to communicate to the remote git repository.

.. code:: bash

    cd /path/to/your/b2share
    git remote add upstream git@github.com:EUDAT-B2SHARE/b2share.git

**Update master branch**

.. code:: bash

    git checkout master
    git fetch upstream
    git merge upstream/master

*NOTE: when you've got pending commits, an error will be thrown*

**Update other branches**

In this case branch 1.0 is merged, however you can replace this with any
branch you want.

.. code:: bash

    git checkout 1.0
    git fetch upstream
    git merge upstream/1.0

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests and must not decrease test coverage.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring.
3. The pull request should work for Python 3.3, 3.4 and 3.5. Check
   https://travis-ci.org/EUDAT-B2SHARE/b2share/pull_requests
   and make sure that the tests pass for all supported Python versions.

Pull-requests should reference any corresponding issue.
Discovered a bug? Create an issue/ ticket first! Your fix
will be targeted at a specific version of B2SHARE only. The ``master``
branch contains the latest and greatest features, whereas ``x.x``
(currently 1.0) is the latest stable version. Bug fixes found on
production, QA or test servers are only pushed to the ``x.x`` branch.

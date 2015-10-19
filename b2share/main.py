# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.


from invenio_base.manage import manager
from invenio_ext.script import register_manager


def main():
    """Run manager."""
    register_manager(manager)

    app = manager.app
    app.name = "b2share"

    @app.errorhandler(401)
    def error_unauthorized(error):
       return "Unauthorized, please login", error.code

    @app.errorhandler(404)
    def error_page_not_found(error):
        return "Page not found", error.code

    @app.errorhandler(405)
    def error_method_not_supported(error):
        return "Method not supported", error.code

    # import ipdb; ipdb.set_trace()
    manager.run()


if __name__ == "__main__":
    main()

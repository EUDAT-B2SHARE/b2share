# -*- coding: utf-8 -*-


from flask import Blueprint, g, request, redirect, url_for, current_app


blueprint = Blueprint('b2share_accounts', __name__, url_prefix="",
                      template_folder='templates',
                      static_url_path='',  # static url path has to be empty
                                           # if url_prefix is empty
                      static_folder='static')

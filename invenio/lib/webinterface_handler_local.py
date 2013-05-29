def customize_app(app):
    #Remove help from top menu
    del app.config['menubuilder_map']['main'].children['help']

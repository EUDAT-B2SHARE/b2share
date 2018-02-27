# General

The B2SHARE web UI is a Single Page Application, based on react and on a custom "flux" architecture. It uses the following libraries:

    - react-router, for routing URLs on the client side
    - react-widgets and react-toggle for widgets (mostly used when editing records)
    - a customized bootstrap theme, but only the css part
    - immutable.js, which is used for defining an immutable data store
    - reqwest.js, for the asynchronous ajax calls to the server
    - moment.js, for simple manipulation and formatting of time

Some libraries are also used, for very specific purposes (computing a json patch, icons)

The flux architecture style is implemented in a custom way by the B2SHARE UI:

    1. a user event or page load event trigger an ajax query from the server
        - all server events are handled in src/data/server.js
    2. the callback of the ajax call places the data returned from the server in an immutable data store
    3. each update of the data store automatically triggers a new repaint of the application
        - see src/main.jsx, updateStateOnTick in AppFrame
    4. the application repaint uses the data from the store as parameters for the react components

Therefore a user event very rarely changes local state of the react components, but usually just calls some function in server.js, which will asynchronously eventually change the data store, which will trigger a repaint, so the user would get a refreshed view.

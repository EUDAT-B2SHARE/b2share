#!/bin/bash
echo Copying files...

CSS_DIR=app/lib/
FONTS_DIR=app/fonts/

mkdir -p $CSS_DIR $FONTS_DIR

cp node_modules/bootstrap/dist/css/* $CSS_DIR
cp node_modules/bootstrap/dist/fonts/* $FONTS_DIR

cp node_modules/font-awesome/css/* $CSS_DIR
cp node_modules/font-awesome/fonts/*  $FONTS_DIR

# cp node_modules/pluralize/pluralize.js $JS_DIR
# cp node_modules/react/dist/react-with-addons.* $JS_DIR
# cp node_modules/react-dom/dist/react-dom.* $JS_DIR

#!/bin/bash
echo Copying files...

CSS_DIR=app/lib/css
FONTS_DIR=app/lib/fonts
IMG_DIR=app/lib/img

mkdir -p $CSS_DIR $FONTS_DIR $IMG_DIR

cp node_modules/bootstrap/dist/css/*   $CSS_DIR/
cp node_modules/bootstrap/dist/fonts/* $FONTS_DIR/

cp node_modules/font-awesome/css/*   $CSS_DIR/
cp node_modules/font-awesome/fonts/* $FONTS_DIR/

cp node_modules/react-toggle/style.css $CSS_DIR/toggle-style.css

cp -r node_modules/react-widgets/dist/css/*   $CSS_DIR/
cp -r node_modules/react-widgets/dist/fonts/* $FONTS_DIR/
cp -r node_modules/react-widgets/dist/img/*   $IMG_DIR/

# cp node_modules/pluralize/pluralize.js $JS_DIR
# cp node_modules/react/dist/react-with-addons.* $JS_DIR
# cp node_modules/react-dom/dist/react-dom.* $JS_DIR

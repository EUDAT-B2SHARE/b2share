var path = require('path');
var webpack = require('webpack');

module.exports = {
    entry: './webpack-main.js',
    output: { path: __dirname+"/app", filename: 'b2share-bundle.js' },
    devtool: 'inline-source-map',
    module: {
        loaders: [
            {   test: /.jsx?$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                query: { presets: ['es2015', 'react'] }
            }
        ]
    }
};

var path = require('path');
var webpack = require('webpack');
const Dotenv = require('dotenv-webpack');
var WatchTimePlugin = require('webpack-watch-time-plugin');

console.log("Using configuration file from", __dirname+'/../webui.cfg');

module.exports = {
    entry: ['./src/main.jsx'],
    devtool: 'cheap-module-eval-source-map',
    output: { path: __dirname+"/app", filename: 'b2share-bundle.js' },
    plugins: [
        // Note: Only values used in source code will be included in the bundle.
        // See dotenv-webpack documentation for more details.
        new Dotenv({
            path: __dirname+'/../webui.cfg', // load this file instead of '.env'.
            systemvars: true, // load environment variables from 'process.env'.
        }),
        WatchTimePlugin
    ],
    module: {
        loaders: [
            {   test: /\.jsx?$/,
                loader: 'babel-loader',
                query: { presets: ['es2015', 'react'] },
                include: path.join(__dirname, 'src')
            }
        ]
    }
};


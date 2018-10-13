var path = require('path');
var webpack = require('webpack');
const Dotenv = require('dotenv-webpack');

console.log("Using configuration file from", __dirname+'/../webui.cfg');

module.exports = {
    entry: ['./src/main.jsx'],
    devtool: 'source-map',
    output: { path: __dirname+"/app", filename: 'b2share-bundle.js' },
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                'NODE_ENV': JSON.stringify('production')
            }
        }),
        // Note: Only values used in source code will be included in the bundle.
        // See dotenv-webpack documentation for more details.
        new Dotenv({
            path: __dirname+'/../webui.cfg', // load this file instead of '.env'.
            systemvars: true, // load environment variables from 'process.env'.
        }),
        new webpack.ContextReplacementPlugin(/moment[\/\\]locale$/, /en/), // trim down moment.js
        new webpack.optimize.OccurenceOrderPlugin(),
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.UglifyJsPlugin({
            compressor: {
                warnings: false
            }
        }),
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

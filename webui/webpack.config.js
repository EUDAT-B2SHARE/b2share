var path = require('path');
var webpack = require('webpack');
var WebpackShellPlugin = require('webpack-shell-plugin');

module.exports = {
    entry: ['./src/main.jsx'],
    devtool: 'source-map',
    output: { path: __dirname+"/app", filename: 'b2share-bundle.js' },
    plugins: [
        new WebpackShellPlugin({onBuildStart:['./make_version_js.sh']}),
        new webpack.DefinePlugin({
            'process.env': {
                'NODE_ENV': JSON.stringify('production')
            }
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

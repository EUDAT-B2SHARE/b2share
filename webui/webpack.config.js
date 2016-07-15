var path = require('path');
var webpack = require('webpack');
var WebpackShellPlugin = require('webpack-shell-plugin');

module.exports = {
    entry: ['./src/main.jsx'],
    devtool: 'source-map',
    output: { path: __dirname+"/app", filename: 'b2share-bundle.js' },
    plugins: [
        new webpack.optimize.OccurenceOrderPlugin(),
        new webpack.DefinePlugin({
            'process.env': {
                'NODE_ENV': JSON.stringify('production')
            }
        }),
        new webpack.optimize.UglifyJsPlugin({
            compressor: {
                warnings: false
            }
        }),
        new WebpackShellPlugin({onBuildStart:['./make_version_js.sh']})
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

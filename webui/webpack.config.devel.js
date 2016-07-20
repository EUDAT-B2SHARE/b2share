var path = require('path');
var webpack = require('webpack');
var WebpackShellPlugin = require('webpack-shell-plugin');

module.exports = {
    entry: ['./src/main.jsx'],
    devtool: 'cheap-module-eval-source-map',
    output: { path: __dirname+"/app", filename: 'b2share-bundle.js' },
    plugins: [
        new WebpackShellPlugin({onBuildStart:['./make_version_js.sh']})
    ],
    resolve: { extensions: ['', '.js', '.jsx', '.json'] },    
    module: {
        loaders: [
            {   test: /\.jsx?$/,
                loader: 'babel-loader',
                query: { presets: ['es2015', 'react'] },
                include: path.join(__dirname, 'src')
            },
            {   test: /\.json?$/, 
                loader: 'json', 
                query: { presets: ['es2015', 'react'] },
                include: path.join(__dirname, 'src')
            }
        ]
    }
};

var path = require('path');
var webpack = require('webpack');

module.exports = {
    entry: ['./src/main.jsx'],
    devtool: 'cheap-module-eval-source-map',
    output: { path: __dirname+"/app", filename: 'b2share-bundle.js' },
    plugins: [
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

var path = require('path');
var webpack = require('webpack');
const Dotenv = require('dotenv-webpack');
var WatchTimePlugin = require('webpack-watch-time-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

console.log("Using configuration file from", __dirname+'/../webui.cfg');

let cleanOptions = {
  root: __dirname+'/app',
  verbose: true,
  dry: false
}


module.exports = {
    entry: ['./src/main.jsx'],
    devtool: 'cheap-module-eval-source-map',
    output: { path: __dirname+"/app/", filename: 'js/b2share-bundle.[hash].js'},
    plugins: [
        // Note: Only values used in source code will be included in the bundle.
        // See dotenv-webpack documentation for more details.
        new Dotenv({
            path: __dirname+'/../webui.cfg', // load this file instead of '.env'.
            systemvars: true, // load environment variables from 'process.env'.
        }),
        WatchTimePlugin,
        new CleanWebpackPlugin('js', cleanOptions),
        //inject false prevents script tag from being automatically injected
        //the script tag is injected directly in index_template.html code instead
        new HtmlWebpackPlugin({
            inject: false,
            hash: false,
            template: 'templates/index_template.html',
            filename: 'index.html'
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

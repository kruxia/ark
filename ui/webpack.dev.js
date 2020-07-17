const path = require('path');

module.exports = {
    entry: {
        app: './src/index.js'
    },
    output: {
        filename: "app.js",
        path: path.resolve(__dirname, 'dist'),
        publicPath: "/",
    },
    mode: 'development',
    devtool: 'source-map',
    devServer: {
        port: 3000,
        open: false,
        historyApiFallback: {
            index: 'index.html',
        },
        contentBase: 'dist',
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                }
            }
        ],
    },
};

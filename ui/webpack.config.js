const path = require('path');
const {DefinePlugin} = require('webpack');

module.exports = {
    entry: './src/index.js',
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist/static'),
    },
    plugins: [
        new DefinePlugin({
            API_URL: JSON.stringify(process.env.API_URL),
            ARCHIVE_URL: JSON.stringify(process.env.ARCHIVE_URL),
        })
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /\/node_modules\//,
                use: {
                    loader: 'babel-loader'
                }
            }],
    },
};

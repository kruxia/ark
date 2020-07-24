const path = require('path');
const {DefinePlugin} = require('webpack');

module.exports = (env) => {
    console.log("ARCHIVE_URL=" + process.env.ARCHIVE_URL);
    console.log("API_URL=" + process.env.API_URL);
    return {
        entry: {
            app: './src/index.js'
        },
        output: {
            filename: "main.js",
            path: path.resolve(__dirname, 'dist/static'),
            publicPath: "/",
        },
        plugins: [
            new DefinePlugin({
                API_URL: JSON.stringify(process.env.API_URL),
                ARCHIVE_URL: JSON.stringify(process.env.ARCHIVE_URL),
            })
        ],
        mode: 'development',
        devtool: 'source-map',
        devServer: {
            port: 3000,
            open: false,
            historyApiFallback: {
                index: 'index.html',
                disableDotRule: true,
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
}
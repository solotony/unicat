//const path = import('path')
const path = require('path')
const HTMLWebpackPlugin = require('html-webpack-plugin')
const {CleanWebpackPlugin} = require('clean-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');

const isDev = process.env.NODE_ENV === 'development'
const isProd = !isDev
console.log('isDev=', isDev)

const optimization = () => {
    const config = {
        splitChunks: {
            chunks: 'all'
        }
    }
    if (isProd) {
        config.minumizer = [
            new OptimizeCssAssetsPlugin(),
            new TerserPlugin()
        ]
    }
    return config
}

const cssLoaders = (extra) => {
    const loaders = [
        {
            loader: MiniCssExtractPlugin.loader,
            options: {
                hmr: true,
                reloadAll: true,
                publicPath: '/static/css/',
                path: path.resolve(__dirname, 'website/static/css'),
            }
        },
        // {
        //     loader: 'style-loader', // inject CSS to page
        // },
        {
            loader: 'css-loader', // translates CSS into CommonJS modules
        }
    ]

    if (extra) {
        if (Array.isArray(extra)) {
            for (i=0; i<extra.length; i++){
                loaders.push(extra[i])
            }
        }
        else
        {
            loaders.push(extra)
        }
    }

    return loaders

}

module.exports = {
    context: path.resolve(__dirname, './website/src'),
    mode: 'development', // production
    entry: {
        main: './index.js',
        analytics: './analytics.js',
    },
    output: {
        filename: '[name].[contenthash].js',
        chunkFilename: "[name].[contenthash].js",
        library: 'huyabrary',
        path: path.resolve(__dirname, 'website/static/js'),
        publicPath: '/static/js/'
    },
    devServer: {
        publicPath: '/static/js/'
    },
    resolve: {
        alias: {
            'Post': './Post.js'
        }
    },
    optimization: optimization(),
    plugins: [
        new HTMLWebpackPlugin({
            template: './index.html',
            filename: path.resolve(__dirname, 'website/static/index.html'),
            minify: false
        }),
        new HTMLWebpackPlugin({
            template: './layout.html',
            filename: path.resolve(__dirname, 'website/templates/layout/layout.html'),
            minify: false
        }),
        // new HTMLWebpackPlugin({
        //     template: './layout-cl.html',
        //     filename: path.resolve(__dirname, 'website/templates/layout/layout-cl.html'),
        //     minify: false
        // }),
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin({
            filename: '[name].[contenthash].css',
            chunkFilename: '[id].css',
        }),
    ],
    module: {
        rules: [
            {
                test: /\.(css)$/,
                use: cssLoaders()
            },
            {
                test: /\.(scss)$/,
                use: cssLoaders([
                    {
                        loader: 'postcss-loader', // Run post css actions
                        options: {
                            plugins: function () { // post css plugins, can be exported to postcss.config.js
                                return [
                                    require('precss'),
                                    require('autoprefixer')
                                ];
                            }
                        }
                    },
                    {
                        loader: 'sass-loader' // compiles Sass to CSS
                    }
                ])
            },
            {
                test: /\.(png|jpg|jpeg|gif|svg)$/,
                use: ['file-loader']
            },
        ]
    }
}
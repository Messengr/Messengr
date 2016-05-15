## End-to-end encryption messaging app with search capabilities

This project implements a proof-of-concept app that provides strong end-to-end encryption for chats and allows users to search through their encrypted messages without the server learning the contents any message nor what the user searched for.

## Motivation

Recently, WhatsApp, a popular messaging app, introduced end-to-end encryption capabilities for messages sent on its service. End-to-End encryption is great because it makes it impossible for the provider to learn the contents of the messages sent. However, while this improves privacy it forces the service to limit some potential functionality such as allowing the user to search through their messages on the server. If the user can't store all of the messages sent locally then the user loses the ability to search through those messages. We would like to introduce a web app that allows users to send messages to each other, encrypted end-to-end, but with the added ability of searching through their messages. By implementing a simplified version of the searchable encryption scheme in "Practical Dynamic Searchable Encryption with Small Leakage" (http://eprint.iacr.org/2013/832.pdf), we aim to provide this searching capability to an end-to-end encryption web messaging app.

## Installation

Install the pre-requisites. You can install them either globally or in [a virtualenv](https://virtualenv.pypa.io/en/latest/), as you prefer. To install via Pip:

```
pip install -r requirements.txt
```
Set the environment variable `APP_SETTINGS` to either config.DevelopmentConfig, which will use the database at `/tmp/test.db` (you will have to create this database first), or config.ProductionConfig, which will use the database with URL set to the environment variable `DATABASE_URL`, which is unset by default.

## License

MIT License

Copyright (c) 2016, Marcos Pertierra, Dennis Garcia, Anthony Erb Lugo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

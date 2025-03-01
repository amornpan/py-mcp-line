# Python LINE MCP Server

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/amornpan/py-mcp-line)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/MCP-1.2.0-green.svg)](https://github.com/modelcontextprotocol)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-teal.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A Model Context Protocol server implementation in Python that provides access to LINE Bot messages. This server enables Language Models to read and analyze LINE conversations through a standardized interface.

## Features

### Core Functionality
* Asynchronous operation using Python's `asyncio`
* Environment-based configuration using `python-dotenv`
* Comprehensive logging system
* LINE Bot webhook event handling
* Message storage in JSON format
* FastAPI integration for API endpoints
* Pydantic models for data validation
* Support for text, sticker, and image messages

## Prerequisites

* Python 3.8+
* Required Python packages:
  * fastapi
  * pydantic
  * python-dotenv
  * mcp-server
  * line-bot-sdk
  * uvicorn

## Installation

```bash
git clone https://github.com/amornpan/py-mcp-line.git
cd py-mcp-line
pip install -r requirements.txt
```

## Project Structure

```
PY-MCP-LINE/
├── src/
│   └── line/
│       ├── __init__.py
│       └── server.py
├── data/
│   └── messages.json
├── tests/
│   ├── __init__.py
│   └── test_line.py
├── .env
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
└── requirements.txt
```

### Directory Structure Explanation
* `src/line/` - Main source code directory
  * `__init__.py` - Package initialization
  * `server.py` - Main server implementation
* `data/` - Data storage directory
  * `messages.json` - Stored LINE messages
* `tests/` - Test files directory
  * `__init__.py` - Test package initialization
  * `test_line.py` - LINE functionality tests
* `.env` - Environment configuration file (not in git)
* `.env.example` - Example environment configuration
* `.gitignore` - Git ignore rules
* `README.md` - Project documentation
* `Dockerfile` - Docker configuration
* `requirements.txt` - Project dependencies

## Configuration

Create a `.env` file in the project root:

```env
LINE_CHANNEL_SECRET=your_channel_secret
LINE_ACCESS_TOKEN=your_access_token
SERVER_PORT=8000
MESSAGES_FILE=data/messages.json
```

## API Implementation Details

### Resource Listing
```python
@app.list_resources()
async def list_resources() -> list[Resource]
```
* Lists available message types from the LINE Bot
* Returns resources with URIs in the format `line://<message_type>/data`
* Includes resource descriptions and MIME types

### Resource Reading
```python
@app.read_resource()
async def read_resource(uri: AnyUrl) -> str
```
* Reads messages of the specified type
* Accepts URIs in the format `line://<message_type>/data`
* Returns messages in JSON format
* Supports filtering by date, user, or content

## Usage with Claude Desktop

Add to your Claude Desktop configuration:

On MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "line": {
      "command": "python",
      "args": [
        "server.py"
      ],
      "env": {
        "LINE_CHANNEL_SECRET": "your_channel_secret",
        "LINE_ACCESS_TOKEN": "your_access_token",
        "SERVER_PORT": "8000",
        "MESSAGES_FILE": "data/messages.json"
      }
    }
  }
}
```

## Error Handling

The server implements comprehensive error handling for:
* Webhook validation failures
* Message storage errors
* Resource access errors
* URI validation
* LINE API response errors

All errors are logged and returned with appropriate error messages.

## Security Features

* Environment variable based configuration
* LINE message signature validation
* Proper error handling
* Input validation through Pydantic

## Contact Information

### Amornpan Phornchaicharoen

[![Email](https://img.shields.io/badge/Email-amornpan%40gmail.com-red?style=flat-square&logo=gmail)](mailto:amornpan@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Amornpan-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/amornpan/)
[![HuggingFace](https://img.shields.io/badge/🤗%20Hugging%20Face-amornpan-yellow?style=flat-square)](https://huggingface.co/amornpan)
[![GitHub](https://img.shields.io/badge/GitHub-amornpan-black?style=flat-square&logo=github)](https://github.com/amornpan)

Feel free to reach out to me if you have any questions about this project or would like to collaborate!

---
*Made with ❤️ by Amornpan Phornchaicharoen*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Amornpan Phornchaicharoen

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Requirements

Create a `requirements.txt` file with:

```
fastapi>=0.104.1
pydantic>=2.10.6
uvicorn>=0.34.0 
python-dotenv>=1.0.1
line-bot-sdk>=3.5.0
anyio>=4.5.0
mcp==1.2.0
```

These versions have been tested and verified to work together. The key components are:
* `fastapi` and `uvicorn` for the API server
* `pydantic` for data validation
* `line-bot-sdk` for LINE Bot integration
* `mcp` for Model Context Protocol implementation
* `python-dotenv` for environment configuration
* `anyio` for asynchronous I/O support

## Acknowledgments

* LINE Developers for the LINE Messaging API
* Model Context Protocol community
* Python FastAPI community
* Contributors to the python-dotenv project
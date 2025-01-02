#  Example Code
This repo contains the sample code for the article - **Mocking vs Patching vs Stubbing**

# Requirements
* Python (3.10.6)

Please install the dependencies via the `requirements.txt` file using 
```bash
pip install -r requirements.txt
```
If you don't have Pip installed, please follow instructions online on how to do it.

# How To Run the Unit Tests
To run the Unit Tests from the root of the repo, run
```bash
pytest -v
```

# asyncio notes
- Define coroutine prefixed "async"
- If a func (coroutine) behaviors like IO-block call (calls to remote, open file, sleep or queue operations), use it after "await" keyword.
- on "await", control returns to event loop to schedule other cooroutines. If available will be scheduled to run while blocking call is being waited.

# Set up remote debug
- Create remote debug config in .vscode/launch.json (Shft+Ctl+P) | Debug: Add Configuration | Python Debugger
- Start the script from bash git:
```
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client src/async_stream.py
```
-  Debug view in Visual Studio Code. Select the "Python Debugger: Remote Attach" configuration. Click the green play button to start debugging.

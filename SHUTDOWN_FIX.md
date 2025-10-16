# Backend Shutdown Fix - Exit Code 15

## Problem
The application was showing exit code 15 when shutting down, which indicates SIGTERM (termination signal) that wasn't handled gracefully. This made it appear as if the backend crashed when it was actually just being terminated.

## Solution Implemented

### 1. **Backend Signal Handling (`run_server.py`)**
- Added proper signal handlers for `SIGTERM` and `SIGINT`
- Implemented graceful shutdown function that properly exits with code 0
- Made the server instance global so signal handlers can access it
- Now exits with code 0 instead of code 15 when receiving termination signals

### 2. **Improved Shutdown Endpoint (`main.py`)**
- Enhanced the `/shutdown` endpoint to properly shut down the server
- Uses `asyncio.create_task()` for better async handling
- Adds a 0.5-second delay to ensure the response is sent before shutdown
- Includes better logging for shutdown operations

### 3. **Electron Process Handling (`main.js`)**
- Updated the backend process close handler to recognize exit code 15 as normal
- Exit codes 0, null, and 15 are now treated as graceful shutdowns
- Added better error handling to prevent duplicate cleanup calls
- Improved timeout handling with proper cleanup

### 4. **Enhanced Will-Quit Event (`main.js`)**
- Added `isShuttingDown` flag to prevent duplicate cleanup
- Better error handling throughout the shutdown sequence
- Properly exits with code 0 instead of calling `app.exit()` without arguments
- More robust SIGTERM fallback handling with try-catch blocks

## Changes Made

### Files Modified:
1. `backend/run_server.py`
2. `backend/main.py`
3. `main.js`

## Testing
To verify the fix:
1. Start the application
2. Close the application normally
3. Check the console logs - should see "Backend shutdown gracefully (SIGTERM)"
4. No error dialogs should appear
5. Backend should exit cleanly with code 0 or 15 (both are now normal)

## Technical Details

**Exit Code 15**: On Windows, this corresponds to SIGTERM (signal 15), which is a normal termination signal. The application now properly handles this signal and exits gracefully.

**Signal Handlers**: Python signal handlers are now registered for both SIGTERM and SIGINT, ensuring the application can shut down properly when these signals are received.

**Graceful Shutdown Flow**:
1. Electron calls the `/shutdown` endpoint
2. Backend sends response with status "ok"
3. After 0.5 seconds, backend sends SIGTERM to itself
4. Signal handler catches SIGTERM and sets `server.should_exit = True`
5. Server shuts down gracefully
6. Process exits with code 0

## Benefits
- No more "Backend Crashed" error dialogs on normal shutdown
- Cleaner application exit
- Better logging of shutdown process
- More reliable cleanup of resources

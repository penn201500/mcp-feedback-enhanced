# MCP Feedback Enhanced - Testing Guide

## 🧪 Testing Persistent Connection Features

This guide helps you test the network resilience and persistent connection features to ensure they work correctly in your environment.

## 📋 Pre-Testing Setup

### 1. Install Latest Version
```bash
# Install the latest version with persistent connection features
pip install uv
uvx mcp-feedback-enhanced@latest version
```

### 2. Enable Debug Mode (Optional)
```bash
export MCP_DEBUG=true
```

## 🔄 Test Scenarios

### **Test 1: Before Fix - Reproduce the Disconnect Issue**

This test reproduces the original network disconnect problem you experienced.

```bash
# 1. Start MCP server in standard mode (without persistence)
uvx mcp-feedback-enhanced@latest test --web

# 2. When the Web UI opens, do NOT provide feedback yet
# 3. Simulate network issues:
#    - Turn WiFi off for 10-15 seconds, then turn back on
#    - Or disconnect/reconnect ethernet cable
#    - Or switch WiFi networks

# Expected Result (BEFORE FIX):
# ❌ You should see "Connection failed" error
# ❌ Request ID error similar to: 10742155-9a5a-46fe-90b6-3a113413db88
# ❌ Session is lost and cannot be recovered
# ❌ Must restart manually
```

### **Test 2: After Fix - Test Persistent Connection**

This test validates the new persistent connection features.

```bash
# 1. Start MCP server in persistent mode
uvx mcp-feedback-enhanced@latest test --persistent

# Or alternatively:
uvx mcp-feedback-enhanced@latest persistent

# 2. When the Web UI opens, do NOT provide feedback yet
# 3. Simulate the same network issues:
#    - Turn WiFi off for 10-15 seconds, then turn back on
#    - Or disconnect/reconnect ethernet cable

# Expected Result (AFTER FIX):
# ✅ Connection automatically recovers
# ✅ Session state is preserved
# ✅ Web UI remains functional
# ✅ Can continue providing feedback normally
# ✅ No manual restart required
```

### **Test 3: Network Resilience Stress Test**

```bash
# Run the dedicated network testing script
cd mcp-feedback-enhanced
python src/mcp_feedback_enhanced/test_network_resilience.py

# Expected Output:
# 🧪 Testing Persistent Connection Resilience
# ✅ Session created: [UUID]
# 💓 Starting connection heartbeat...
# 🔌 Simulating network disconnect for 15.0 seconds...
# 🔄 Testing connection loss handling...
# ✅ Connection loss handled successfully
# 🔌 Network reconnected
# 📂 Testing session restoration...
# ✅ Session restored successfully
```

### **Test 4: Interactive Manual Testing**

```bash
# Start interactive test mode
python src/mcp_feedback_enhanced/test_network_resilience.py interactive

# This will start persistent mode and wait for manual testing
# You can then manually:
# 1. Disconnect WiFi
# 2. Switch networks
# 3. Disconnect ethernet
# 4. Test various network scenarios

# Watch the heartbeat messages to confirm connection persistence
```

## 🛠️ Advanced Testing

### **Test Session Management Tools**

After setting up persistent mode, you can test the session management features:

```bash
# In your AI client (like Cursor), call these MCP tools:

# 1. List active sessions
manage_persistent_sessions(action="list")

# 2. After a disconnect, restore a session
manage_persistent_sessions(action="restore", session_id="[SESSION_ID]")

# 3. Clean up old sessions
manage_persistent_sessions(action="cleanup", max_age_hours=24)
```

### **Test Configuration Options**

Test different environment variable combinations:

```bash
# Test 1: Basic persistent mode
MCP_PERSISTENT=true uvx mcp-feedback-enhanced@latest

# Test 2: Persistent + Debug mode
MCP_PERSISTENT=true MCP_DEBUG=true uvx mcp-feedback-enhanced@latest

# Test 3: Persistent + Force Web UI
MCP_PERSISTENT=true FORCE_WEB=true uvx mcp-feedback-enhanced@latest
```

## 📊 Comparison Results

### **Before Fix (Standard Mode)**
| Scenario | Result | Recovery Time | Manual Action Required |
|----------|--------|---------------|------------------------|
| WiFi disconnect (10s) | ❌ Connection lost | N/A | Yes - restart required |
| Network switch | ❌ Session terminated | N/A | Yes - restart required |
| Timeout (10 min) | ❌ Server stops | N/A | Yes - restart required |
| VPN disconnect | ❌ Connection failed | N/A | Yes - restart required |

### **After Fix (Persistent Mode)**
| Scenario | Result | Recovery Time | Manual Action Required |
|----------|--------|---------------|------------------------|
| WiFi disconnect (10s) | ✅ Auto-recovery | 5-15 seconds | No |
| Network switch | ✅ Reconnects | 5-20 seconds | No |
| Timeout (10 min) | ✅ Extended timeout (24h) | N/A | No |
| VPN disconnect | ✅ Auto-recovery | 5-15 seconds | No |

## 🔍 Troubleshooting Tests

### **Test Debug Logging**

```bash
# Enable detailed logging to diagnose issues
MCP_DEBUG=true MCP_PERSISTENT=true uvx mcp-feedback-enhanced@latest

# Look for these log messages:
# ✅ "Persistent mode enabled via environment variable"
# ✅ "ConnectionManager initialized"
# ✅ "Starting connection heartbeat"
# ✅ "Created persistent session: [UUID]"
# ✅ "Heartbeat: Connection alive"
```

### **Test Session Storage**

```bash
# Check if sessions are being saved
ls -la ~/.cache/mcp-feedback-enhanced/sessions/

# Should see JSON files with session data
cat ~/.cache/mcp-feedback-enhanced/sessions/[SESSION-ID].json
```

### **Test Recovery After System Sleep**

```bash
# 1. Start persistent mode
MCP_PERSISTENT=true uvx mcp-feedback-enhanced@latest

# 2. Put your Mac to sleep
sudo pmset sleepnow

# 3. Wake up after 30 seconds
# 4. Check if session recovered

# Expected: Session should be restored automatically
```

## 📈 Performance Testing

### **Test Resource Usage**

```bash
# Monitor resource usage in persistent mode
# Start persistent mode in one terminal:
MCP_PERSISTENT=true uvx mcp-feedback-enhanced@latest

# In another terminal, monitor resources:
ps aux | grep mcp-feedback-enhanced
top -p $(pgrep -f mcp-feedback-enhanced)

# Check for memory leaks over time
```

### **Test Multiple Sessions**

```bash
# Test handling multiple concurrent sessions
# Start multiple instances and test session isolation
```

## ✅ Success Criteria

Your persistent connection implementation is working correctly if:

1. **✅ Network Disconnect Recovery**: WiFi off/on cycles are handled automatically
2. **✅ Session Persistence**: Data survives disconnections
3. **✅ Extended Timeouts**: Sessions can run for hours without timing out
4. **✅ Resource Cleanup**: No memory leaks or zombie processes
5. **✅ Session Management**: Can list, restore, and cleanup sessions
6. **✅ Backward Compatibility**: Standard mode still works as before

## 🚨 Failure Indicators

Report issues if you see:

1. **❌ Connection Errors**: Still getting "Connection failed" messages
2. **❌ Session Loss**: Data lost after network interruptions
3. **❌ Resource Leaks**: Memory usage growing over time
4. **❌ Startup Failures**: Persistent mode won't start
5. **❌ Recovery Failures**: Sessions don't restore properly

## 📝 Reporting Test Results

When reporting test results, please include:

1. **Environment**: OS, Python version, network setup
2. **Test Scenario**: Which test you ran
3. **Expected vs Actual**: What you expected vs what happened
4. **Logs**: Relevant debug logs (with `MCP_DEBUG=true`)
5. **Timing**: How long disconnects lasted
6. **Configuration**: Environment variables used

Example report:
```
Environment: macOS 14.5, Python 3.11, WiFi connection
Test: Network disconnect for 15 seconds
Expected: Auto-recovery within 20 seconds
Actual: ✅ Recovered in 8 seconds, session intact
Config: MCP_PERSISTENT=true, MCP_DEBUG=true
```

This testing approach will help you validate that the persistent connection features are working correctly and addressing your original network disconnect issues.

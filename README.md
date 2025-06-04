# MCP Feedback Enhanced

**🌐 Language / 語言切換:** **English** | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

**Original Author:** [Fábio Ferreira](https://x.com/fabiomlferreira) | [Original Project](https://github.com/noopstudios/interactive-feedback-mcp) ⭐
**Enhanced Fork:** [Minidoracat](https://github.com/Minidoracat)
**UI Design Reference:** [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

## 🎯 Core Concept

This is an [MCP server](https://modelcontextprotocol.io/) that implements **human-in-the-loop** workflows in AI-assisted development tools. By guiding AI to confirm with users rather than making speculative operations, it can consolidate up to 25 tool calls into a single feedback-oriented request, dramatically reducing platform costs.

**Supported Platforms:** [Cursor](https://www.cursor.com) | [Cline](https://cline.bot) | [Windsurf](https://windsurf.com)

### 🔄 Workflow
1. **AI Call** → `mcp-feedback-enhanced`
2. **Environment Detection** → Auto-select appropriate interface
3. **User Interaction** → Command execution, text feedback, image upload
4. **Feedback Delivery** → Information returns to AI
5. **Process Continuation** → Adjust or end based on feedback

## 🌟 Key Features

### 🖥️ Dual Interface System
- **Qt GUI**: Native experience for local environments, modular refactored design
- **Web UI**: Modern interface for remote SSH environments, brand new architecture
- **Smart Switching**: Auto-detect environment and choose optimal interface

### 🎨 Brand New Interface Design (v2.1.0)
- **Modular Architecture**: Both GUI and Web UI adopt modular design
- **Centralized Management**: Reorganized folder structure for easier maintenance
- **Modern Themes**: Improved visual design and user experience
- **Responsive Layout**: Adapts to different screen sizes and window dimensions

### 🖼️ Image Support
- **Format Support**: PNG, JPG, JPEG, GIF, BMP, WebP
- **Upload Methods**: Drag & drop files + clipboard paste (Ctrl+V)
- **Auto Processing**: Smart compression to ensure 1MB limit compliance

### 🌏 Multi-language
- **Three Languages**: English, Traditional Chinese, Simplified Chinese
- **Smart Detection**: Auto-select based on system language
- **Live Switching**: Change language directly within interface

## 🖥️ Interface Preview

### Qt GUI Interface (Refactored Version)
<div align="center">
  <img src="docs/images/en/gui1.png" width="400" alt="Qt GUI Main Interface" />
  <img src="docs/images/en/gui2.png" width="400" alt="Qt GUI Settings Interface" />
</div>

*Qt GUI Interface - Modular refactoring, supporting local environments*

### Web UI Interface (Refactored Version)
<div align="center">
  <img src="docs/images/en/web1.png" width="400" alt="Web UI Main Interface" />
  <img src="docs/images/en/web2.png" width="400" alt="Web UI Settings Interface" />
</div>

*Web UI Interface - Brand new architecture, suitable for SSH Remote environments*

**Keyboard Shortcuts**
- `Ctrl+Enter`: Submit feedback (supports both main keyboard and numpad)
- `Ctrl+V`: Directly paste clipboard images

## 🚀 Quick Start

### 1. Installation & Testing
```bash
# Install uv (if not already installed)
pip install uv

# Quick test
uvx mcp-feedback-enhanced@latest test

# Test persistent connection mode
uvx mcp-feedback-enhanced@latest test --persistent
```

### 2. MCP Configuration
**Basic Configuration** (suitable for most users):
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback", "manage_persistent_sessions"]
    }
  }
}
```

**Persistent Connection Configuration** (network resilience):
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest", "persistent"],
      "timeout": 86400,
      "env": {
        "MCP_PERSISTENT": "true",
        "MCP_DEBUG": "false"
      },
      "autoApprove": ["interactive_feedback", "manage_persistent_sessions"]
    }
  }
}
```

**Advanced Configuration** (custom environment needed):
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "env": {
        "FORCE_WEB": "true",
        "MCP_DEBUG": "false",
        "MCP_PERSISTENT": "false"
      },
      "autoApprove": ["interactive_feedback", "manage_persistent_sessions"]
    }
  }
}
```

### 3. Persistent Connection Features

**🔄 Network Resilience**
- Automatic reconnection on network disconnects
- Session state preservation during interruptions
- Extended timeouts for long-running sessions
- Heartbeat monitoring to maintain connections

**📝 Session Management**
```bash
# Start persistent mode
uvx mcp-feedback-enhanced@latest persistent

# List active sessions
# Use manage_persistent_sessions tool with action="list"

# Restore interrupted session
# Use manage_persistent_sessions tool with action="restore" and session_id

# Cleanup old sessions
# Use manage_persistent_sessions tool with action="cleanup"
```

### 4. Prompt Engineering Setup
For best results, add these rules to your AI assistant:

```
# MCP Interactive Feedback Rules

1. During any process, task, or conversation, whether asking, responding, or completing stage tasks, must call MCP mcp-feedback-enhanced.
2. When receiving user feedback, if feedback content is not empty, must call MCP mcp-feedback-enhanced again and adjust behavior based on feedback.
3. Only when user explicitly indicates "end" or "no more interaction needed" can you stop calling MCP mcp-feedback-enhanced, then the process is complete.
4. Unless receiving end command, all steps must repeatedly call MCP mcp-feedback-enhanced.
5. Before completing the task, use the MCP mcp-feedback-enhanced to ask the user for feedback.

# MCP Persistent Connection Rules (Optional - for network resilience)

6. If experiencing network connectivity issues, use manage_persistent_sessions to list and restore previous sessions.
7. In persistent mode, sessions are automatically saved and can be resumed after network interruptions.
```

### 5. Network Disconnect Testing

```bash
# Test network resilience
cd mcp-feedback-enhanced
python src/mcp_feedback_enhanced/test_network_resilience.py

# Interactive testing (manual network disconnect)
python src/mcp_feedback_enhanced/test_network_resilience.py interactive

# Reproduce network jitter issue
# 1. Start persistent mode: uvx mcp-feedback-enhanced@latest persistent
# 2. Manually disconnect WiFi for 10-30 seconds
# 3. Reconnect - session should automatically restore
```

## ⚙️ Advanced Settings

### Environment Variables
| Variable | Purpose | Values | Default |
|----------|---------|--------|---------|
| `FORCE_WEB` | Force use Web UI | `true`/`false` | `false` |
| `MCP_DEBUG` | Debug mode | `true`/`false` | `false` |
| `MCP_PERSISTENT` | Persistent connection mode | `true`/`false` | `false` |
| `INCLUDE_BASE64_DETAIL` | Full Base64 for images | `true`/`false` | `false` |

### Persistent Connection Settings
- **Heartbeat Interval**: 30 seconds (keeps connection alive)
- **Reconnection Delay**: 5 seconds between reconnection attempts
- **Max Reconnection Attempts**: 10 attempts before giving up
- **Session Storage**: `~/.cache/mcp-feedback-enhanced/sessions/`
- **Extended Timeout**: 24 hours for persistent sessions

### Testing Options
```bash
# Version check
uvx mcp-feedback-enhanced@latest version       # Check version

# Interface-specific testing
uvx mcp-feedback-enhanced@latest test --gui    # Quick test Qt GUI
uvx mcp-feedback-enhanced@latest test --web    # Test Web UI (auto continuous running)
uvx mcp-feedback-enhanced@latest test --persistent # Test persistent connection mode

# Persistent mode server
uvx mcp-feedback-enhanced@latest persistent    # Start with persistent connections
uvx mcp-feedback-enhanced@latest server --persistent # Alternative syntax

# Debug mode
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

### Developer Installation
```bash
git clone https://github.com/Minidoracat/mcp-feedback-enhanced.git
cd mcp-feedback-enhanced
uv sync
```

**Local Testing Methods**
```bash
# Method 1: Standard test (recommended)
uv run python -m mcp_feedback_enhanced test

# Method 2: Persistent connection test
uv run python -m mcp_feedback_enhanced test --persistent

# Method 3: Network resilience test
uv run python src/mcp_feedback_enhanced/test_network_resilience.py

# Method 4: Complete test suite (macOS and Windows dev environment)
uvx --with-editable . mcp-feedback-enhanced test

# Method 5: Interface-specific testing
uvx --with-editable . mcp-feedback-enhanced test --gui    # Quick test Qt GUI
uvx --with-editable . mcp-feedback-enhanced test --web    # Test Web UI (auto continuous running)
```

**Testing Descriptions**
- **Standard Test**: Complete functionality check, suitable for daily development verification
- **Persistent Test**: Tests network resilience and session management features
- **Network Resilience Test**: Dedicated script for testing connection recovery
- **Complete Test**: Deep testing of all components, suitable for pre-release verification
- **Qt GUI Test**: Quick launch and test of local graphical interface
- **Web UI Test**: Start Web server and keep running for complete Web functionality testing

## 🆕 Version History

📋 **Complete Version History:** [RELEASE_NOTES/CHANGELOG.en.md](RELEASE_NOTES/CHANGELOG.en.md)

### Latest Version Highlights (v2.3.0)
- 🔄 **Persistent Connection Mode**: Network resilience with automatic reconnection
- 💾 **Session State Preservation**: Sessions survive network interruptions and timeouts
- 🔗 **Connection Manager**: New component for handling connection lifecycle
- 📊 **Session Management Tools**: List, restore, and cleanup persistent sessions
- ⏱️ **Extended Timeouts**: 24-hour timeouts for persistent sessions
- 🩺 **Network Testing**: Dedicated tools for testing connection resilience

### Previous Version (v2.2.2)
- 🔄 **Timeout Auto-cleanup**: Fixed GUI/Web UI not automatically closing after MCP session timeout
- 🛡️ **Resource Management Optimization**: Improved timeout handling mechanism to ensure proper cleanup of all UI resources
- 🎯 **QTimer Integration**: Introduced precise QTimer timeout control mechanism in GUI

## 🐛 Common Issues

**Q: Getting "Connection failed" errors during network interruptions**
A: **NEW**: Enable persistent mode with `MCP_PERSISTENT=true` or use `uvx mcp-feedback-enhanced@latest persistent`. This provides automatic reconnection and session restoration.

**Q: Sessions lost after network disconnect**
A: **NEW**: Use persistent connection mode. Sessions are automatically saved to `~/.cache/mcp-feedback-enhanced/sessions/` and can be restored after reconnection.

**Q: How to test network resilience**
A: **NEW**: Run `python src/mcp_feedback_enhanced/test_network_resilience.py interactive` then manually disconnect/reconnect your network to test the recovery mechanism.

**Q: Getting "Unexpected token 'D'" error**
A: Debug output interference. Set `MCP_DEBUG=false` or remove the environment variable.

**Q: Chinese character garbled text**
A: Fixed in v2.0.3. Update to latest version: `uvx mcp-feedback-enhanced@latest`

**Q: Image upload fails**
A: Check file size (≤1MB) and format (PNG/JPG/GIF/BMP/WebP).

**Q: Web UI won't start**
A: Set `FORCE_WEB=true` or check firewall settings.

**Q: Gemini Pro 2.5 cannot parse images**
A: Known issue. Gemini Pro 2.5 may not correctly parse uploaded image content. Testing shows Claude-4-Sonnet can properly analyze images. Recommend using Claude models for better image understanding capabilities.

**Q: Multi-screen window positioning issues**
A: Fixed in v2.1.1. Go to "⚙️ Settings" tab, check "Always show window at primary screen center" to resolve window positioning issues. Especially useful for T-shaped screen arrangements and other complex multi-monitor configurations.

## 🙏 Acknowledgments

### 🌟 Support Original Author
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)
**Original Project:** [noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)

If you find this useful, please:
- ⭐ [Star the original project](https://github.com/noopstudios/interactive-feedback-mcp)
- 📱 [Follow the original author](https://x.com/fabiomlferreira)

### Design Inspiration
**sanshao85** - [mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

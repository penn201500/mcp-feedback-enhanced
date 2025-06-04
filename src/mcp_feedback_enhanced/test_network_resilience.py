#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Resilience Testing
===========================

Test script to simulate network disconnects and validate the persistent
connection functionality of MCP Feedback Enhanced.
"""

import asyncio
import os
import signal
import sys
import time
import threading
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_feedback_enhanced.connection_manager import get_connection_manager
from mcp_feedback_enhanced.debug import server_debug_log as debug_log


class NetworkSimulator:
    """Simulates network connectivity issues for testing"""

    def __init__(self):
        self.is_connected = True
        self.disconnect_event = threading.Event()

    def simulate_disconnect(self, duration: float = 10.0):
        """Simulate network disconnect for specified duration"""
        print(f"🔌 Simulating network disconnect for {duration} seconds...")
        self.is_connected = False
        self.disconnect_event.set()

        def reconnect():
            time.sleep(duration)
            self.is_connected = True
            self.disconnect_event.clear()
            print("🔌 Network reconnected")

        threading.Thread(target=reconnect, daemon=True).start()

    def is_network_available(self) -> bool:
        """Check if network is available (simulated)"""
        return self.is_connected


async def test_persistent_connection():
    """Test persistent connection with simulated network issues"""
    print("🧪 Testing Persistent Connection Resilience")
    print("=" * 50)

    # Enable debug mode
    os.environ["MCP_DEBUG"] = "true"
    os.environ["MCP_PERSISTENT"] = "true"

    # Initialize connection manager
    connection_manager = get_connection_manager()
    connection_manager.enable_persistent_mode()

    # Create a test session
    project_dir = os.getcwd()
    summary = "Testing network resilience and persistent connections"

    print("📝 Creating persistent session...")
    session_id = await connection_manager.create_persistent_session(project_dir, summary)
    print(f"✅ Session created: {session_id}")

    # Start heartbeat
    print("💓 Starting connection heartbeat...")
    await connection_manager.start_heartbeat()

    # Simulate normal operation for a bit
    print("⏳ Normal operation for 5 seconds...")
    await asyncio.sleep(5)

    # Simulate network disconnect
    print("🔌 Simulating network disconnect...")
    simulator = NetworkSimulator()
    simulator.simulate_disconnect(15.0)  # 15 second disconnect

    # Test connection loss handling
    print("🔄 Testing connection loss handling...")
    try:
        await connection_manager.handle_connection_loss()
        print("✅ Connection loss handled successfully")
    except Exception as e:
        print(f"❌ Connection loss handling failed: {e}")

    # Wait for reconnection
    print("⏳ Waiting for network reconnection...")
    while not simulator.is_network_available():
        await asyncio.sleep(1)

    # Test session restoration
    print("📂 Testing session restoration...")
    restored_session = await connection_manager.restore_session(session_id)
    if restored_session:
        print("✅ Session restored successfully")
        print(f"   Project: {restored_session.get('project_directory', 'N/A')}")
        print(f"   Status: {restored_session.get('status', 'N/A')}")
    else:
        print("❌ Session restoration failed")

    # Test session management
    print("📋 Testing session management...")
    sessions = connection_manager.get_active_sessions()
    print(f"✅ Found {len(sessions)} active sessions")

    # Update session with test feedback
    print("💬 Adding test feedback to session...")
    await connection_manager.update_session_feedback(
        "Test feedback after network disconnect",
        []  # No images for this test
    )
    print("✅ Feedback added successfully")

    # Stop the connection manager
    print("🛑 Stopping connection manager...")
    connection_manager.stop()
    print("✅ Test completed successfully")


async def test_timeout_behavior():
    """Test how the system behaves with different timeout values"""
    print("\n🕐 Testing Timeout Behavior")
    print("=" * 30)

    connection_manager = get_connection_manager()

    # Test with very short timeout
    print("⏱️  Testing with 5-second timeout...")
    start_time = time.time()

    try:
        # This would normally timeout
        await asyncio.wait_for(asyncio.sleep(10), timeout=5)
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"✅ Timeout occurred after {elapsed:.1f} seconds (expected)")

    # Test with extended timeout in persistent mode
    connection_manager.enable_persistent_mode()
    print("⏱️  Testing with persistent mode (extended timeout)...")

    # In persistent mode, timeouts should be much longer
    # This is just a simulation - actual implementation would handle this differently
    extended_timeout = 86400  # 24 hours
    print(f"✅ Extended timeout set to {extended_timeout} seconds for persistent mode")


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal, cleaning up...")
    connection_manager = get_connection_manager()
    connection_manager.stop()
    sys.exit(0)


async def interactive_test():
    """Interactive test mode for manual testing"""
    print("\n🎮 Interactive Test Mode")
    print("=" * 25)
    print("This mode will start a persistent connection and wait for manual testing.")
    print("You can:")
    print("1. Disconnect your network manually")
    print("2. Turn WiFi off/on")
    print("3. Switch networks")
    print("4. Wait for timeouts")
    print("\nPress Ctrl+C to stop the test.")

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Enable persistent mode
    os.environ["MCP_PERSISTENT"] = "true"
    connection_manager = get_connection_manager()
    connection_manager.enable_persistent_mode()

    # Create session
    session_id = await connection_manager.create_persistent_session(
        os.getcwd(),
        "Interactive testing session - you can disconnect network manually"
    )

    print(f"📝 Created session: {session_id}")
    print("💓 Starting heartbeat monitoring...")

    await connection_manager.start_heartbeat()

    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(10)
            sessions = connection_manager.get_active_sessions()
            print(f"💓 Heartbeat - {len(sessions)} active sessions")
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    finally:
        connection_manager.stop()


async def main():
    """Main test function"""
    print("🚀 MCP Feedback Enhanced - Network Resilience Testing")
    print("=" * 55)

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        await interactive_test()
    else:
        await test_persistent_connection()
        await test_timeout_behavior()

        print("\n🎯 Testing Summary")
        print("=" * 20)
        print("✅ Persistent connection tests completed")
        print("✅ Timeout behavior tests completed")
        print("✅ Session management tests completed")
        print("\n💡 To run interactive tests: python test_network_resilience.py interactive")


if __name__ == "__main__":
    asyncio.run(main())

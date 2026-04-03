#!/usr/bin/env python3
"""
Simple ngrok tunnel for exposing FMS backend to public internet.
This allows friends on different networks to access the app.
"""

from pyngrok import ngrok
import time
import sys

# Set up the tunnel
print("🌐 Starting ngrok tunnel...")
print("=" * 60)

try:
    # Open tunnel to port 8000
    public_url = ngrok.connect(8000, "http", bind_tls=True)
    
    print(f"\n✅ Tunnel created successfully!")
    print(f"\n📍 PUBLIC URL: {public_url}")
    print("\n" + "=" * 60)
    print("\n📋 SHARE THIS WITH YOUR FRIEND:\n")
    print(f"Backend URL: {public_url}")
    print("\nFriend should paste this in browser console (F12 → Console):")
    print(f'window.FMS_API_BASE = "{public_url}"; location.reload();')
    print("\n" + "=" * 60)
    print("\n⏱️  Tunnel is active. Press Ctrl+C to stop.\n")
    
    # Keep tunnel alive
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n\n🛑 Stopping tunnel...")
    ngrok.kill()
    print("✓ Tunnel closed.")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

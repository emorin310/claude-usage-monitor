#!/usr/bin/env python3
"""
Monitored Authentication Harvest
Runs the token harvester with built-in monitoring for hangs/crashes
"""

import asyncio
import subprocess
import signal
import os
import time
from datetime import datetime

class MonitoredAuthHarvest:
    def __init__(self):
        self.process = None
        self.start_time = None
        self.max_runtime = 600  # 10 minutes max
        
    def run_with_monitoring(self):
        """Run the auth harvester with monitoring"""
        print("🎯 MONITORED ZEHRS TOKEN HARVESTER")
        print("=" * 45)
        print("⚡ Features:")
        print("  • 10-minute timeout protection")
        print("  • Crash detection and recovery")  
        print("  • Process monitoring")
        print("  • Automatic cleanup")
        print()
        
        # Change to correct directory and activate virtual environment
        script_cmd = [
            'bash', '-c', 
            'cd /home/magi/clawd && source playwright-env/bin/activate && python scripts/auth-token-harvester.py'
        ]
        
        try:
            print("🚀 Starting token harvester process...")
            self.start_time = time.time()
            
            # Start the process with input handling
            self.process = subprocess.Popen(
                script_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"📊 Process started (PID: {self.process.pid})")
            print("🔍 Monitoring output...")
            print("-" * 45)
            
            # Send "1" to choose interactive harvest option
            try:
                self.process.stdin.write("1\n")
                self.process.stdin.flush()
                print("📝 Sent option '1' for interactive harvest")
            except:
                pass
            
            # Monitor the process
            output_lines = []
            last_output_time = time.time()
            
            while True:
                # Check timeout
                runtime = time.time() - self.start_time
                if runtime > self.max_runtime:
                    print(f"\n⏰ TIMEOUT: Process exceeded {self.max_runtime/60:.1f} minutes")
                    self.cleanup_process()
                    return False
                
                # Check if process is still running
                if self.process.poll() is not None:
                    print(f"\n✅ Process completed (exit code: {self.process.returncode})")
                    break
                
                # Read output (non-blocking)
                try:
                    # Use select to check if output is available (Linux)
                    import select
                    ready, _, _ = select.select([self.process.stdout], [], [], 1)
                    
                    if ready:
                        line = self.process.stdout.readline()
                        if line:
                            output_lines.append(line.strip())
                            print(f"📤 {line.strip()}")
                            last_output_time = time.time()
                            
                            # Check for specific prompts and respond
                            if "Press Enter to continue" in line:
                                try:
                                    self.process.stdin.write("\n")
                                    self.process.stdin.flush()
                                    print("📝 Sent Enter to continue")
                                except:
                                    pass
                                    
                            elif "Enter choice" in line:
                                try:
                                    self.process.stdin.write("1\n")
                                    self.process.stdin.flush()
                                    print("📝 Sent choice '1'")
                                except:
                                    pass
                    
                    # Check for no output (potential hang)
                    no_output_time = time.time() - last_output_time
                    if no_output_time > 120:  # 2 minutes without output
                        print(f"\n⚠️ WARNING: No output for {no_output_time:.0f} seconds")
                        if no_output_time > 300:  # 5 minutes = likely hung
                            print("❌ Process appears hung - terminating")
                            self.cleanup_process()
                            return False
                    
                except ImportError:
                    # Fallback for systems without select
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Monitoring error: {e}")
                    break
                    
                time.sleep(1)
            
            # Process completed - check results
            return self.check_results(output_lines)
            
        except KeyboardInterrupt:
            print(f"\n⏹️ Interrupted by user")
            self.cleanup_process()
            return False
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            self.cleanup_process()
            return False
    
    def cleanup_process(self):
        """Clean up the process safely"""
        if self.process and self.process.poll() is None:
            print("🧹 Cleaning up process...")
            try:
                # Try gentle termination first
                self.process.terminate()
                time.sleep(2)
                
                # Force kill if needed
                if self.process.poll() is None:
                    self.process.kill()
                    print("💥 Process force-killed")
                else:
                    print("✅ Process terminated gracefully")
                    
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
    
    def check_results(self, output_lines):
        """Check if the harvest was successful"""
        print("\n" + "=" * 45)
        print("📊 HARVEST RESULTS ANALYSIS")
        print("=" * 45)
        
        # Look for success indicators in output
        success_indicators = [
            "Auth data saved",
            "SUCCESS!",  
            "endpoints working",
            "API ACCESS ACHIEVED"
        ]
        
        error_indicators = [
            "error",
            "failed",
            "timeout", 
            "crash"
        ]
        
        success_found = any(indicator.lower() in " ".join(output_lines).lower() 
                          for indicator in success_indicators)
        
        errors_found = [indicator for indicator in error_indicators 
                       if indicator.lower() in " ".join(output_lines).lower()]
        
        # Check for output files
        token_file = "/home/magi/clawd/grocery-data/api_tokens.json"
        api_files = []
        
        if os.path.exists(token_file):
            print(f"✅ Token file found: {token_file}")
            try:
                import json
                with open(token_file, 'r') as f:
                    data = json.load(f)
                print(f"   📊 Contains: {len(data.get('headers', {}))} auth headers")
                print(f"   📡 API calls: {len(data.get('api_calls', {}))}")
                print(f"   🍪 Auth cookies: {len(data.get('auth_cookies', {}))}")
                success_found = True
            except Exception as e:
                print(f"   ⚠️ Could not read token file: {e}")
        
        # Look for API response files
        data_dir = "/home/magi/clawd/grocery-data"
        if os.path.exists(data_dir):
            api_files = [f for f in os.listdir(data_dir) if f.startswith('api_success_')]
            if api_files:
                print(f"✅ API success files: {len(api_files)}")
                success_found = True
        
        # Summary
        if success_found and not errors_found:
            print("\\n🎉 HARVEST SUCCESSFUL!")
            print("✅ Authentication tokens captured")
            print("🚀 Ready for API automation")
            return True
        elif success_found and errors_found:
            print("\\n⚠️ PARTIAL SUCCESS")
            print(f"✅ Some progress made")
            print(f"❌ Issues: {', '.join(errors_found)}")
            return True
        else:
            print("\\n❌ HARVEST FAILED")
            if errors_found:
                print(f"❌ Errors: {', '.join(errors_found)}")
            print("🔄 May need different approach")
            return False

def main():
    monitor = MonitoredAuthHarvest()
    
    print("🛡️ SAFETY MONITORING ACTIVE")
    print("⏰ Max runtime: 10 minutes")
    print("🔍 Hang detection: 5 minutes")
    print("⚡ Auto-cleanup enabled")
    print()
    
    # Run the monitored harvest
    success = monitor.run_with_monitoring()
    
    if success:
        print("\\n🎯 Next steps:")
        print("1. Test the captured tokens")
        print("2. Implement full API automation") 
        print("3. Build grocery management system")
    else:
        print("\\n🔄 Alternative approaches to try:")
        print("1. Manual session export from browser")
        print("2. Browser extension approach")
        print("3. Email receipt parsing")

if __name__ == "__main__":
    main()
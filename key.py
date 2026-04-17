import plistlib
import base64

def extract_signal_ios_key(plist_path):
    with open(plist_path, 'rb') as f:
        data = plistlib.load(f)
    
    # Cellebrite usually nests items under 'keychainEntries'
    entries = data.get('keychainEntries', [])
    
    for entry in entries:
        # Check all values in the entry for Signal-related strings
        entry_values = [str(val) for val in entry.values()]
        if any("org.whispersystems.signal" in v or "GRDB" in v for v in entry_values):
            
            # Found a Signal entry, now look for the data blob (usually 32 bytes)
            for k, v in entry.items():
                if isinstance(v, bytes) and len(v) == 32:
                    print(f"--- Signal Key Found ---")
                    print(f"Service: {entry.get('svce') or entry.get('Service')}")
                    print(f"Account: {entry.get('acct') or entry.get('Account')}")
                    print(f"Hex Key: 0x{v.hex()}")
                    print("-" * 24)
                    return v.hex()
                    
    print("Signal key not found in this plist.")
    return None

extract_signal_ios_key('backup_keychain_v2.plist')

import requests
import json

try:
    # 1. Get App ID
    resp = requests.get("http://localhost:4040/api/v1/applications")
    apps = resp.json()
    if not apps:
        print("No apps found.")
        exit()
        
    app_id = apps[0]['id']
    print(f"App ID: {app_id}")
    
    # 2. Get Executors
    exec_url = f"http://localhost:4040/api/v1/applications/{app_id}/executors"
    print(f"Fetching: {exec_url}")
    
    r = requests.get(exec_url)
    data = r.json()
    
    if data:
        print("First Executor Keys:")
        print(json.dumps(list(data[0].keys()), indent=2))
        print("\nFirst Executor Data:")
        print(json.dumps(data[0], indent=2))
    else:
        print("No executor data found.")
        
except Exception as e:
    print(f"Error: {e}")

import httpx

def check_url(name, url):
    try:
        r = httpx.get(url, timeout=2.0)
        print(f"✅ {name}: {url} (Status: {r.status_code})")
        return True
    except Exception as e:
        print(f"❌ {name}: {url} (Error: {type(e).__name__})")
        return False

print("--- AI News Analyzer Local Dev Health Check ---")
be_docs = check_url("Backend Docs", "http://localhost:8000/docs")
be_health = check_url("Backend Health", "http://localhost:8000/api/v1/health")
fe_app = check_url("Frontend App", "http://localhost:3000")

print("\n--- Summary ---")
if be_docs and be_health and fe_app:
    print("STATUS: ALL SYSTEMS GO 🚀")
    print("Note: Always use port 8000 for backend API calls in local dev.")
else:
    print("STATUS: SOME SYSTEMS DOWN ⚠️")
    print("Run 'make dev-local' to start both servers.")

import uvicorn
import os
import sys

def main():
    """Run the FastAPI server"""
    print("=" * 50)
    print("Starting Multi-Agent Game Tester POC Server")
    print("=" * 50)
    print(f"Server will be available at: http://localhost:8000")
    print("Press CTRL+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Server stopped by user")
        print("=" * 50)
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
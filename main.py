"""
FastAPI Server Entry Point

This script provides the main entry point for running the FastAPI server
with Uvicorn in development and production environments.
"""

import sys
import uvicorn
from src.api.app_factory import get_app_factory, create_configured_app
from src.utilities.logger import Logger


def main():
    """Main entry point for the FastAPI server."""
    logger = Logger("fastapi_main")
    
    try:
        # Create application factory and get server configuration
        app_factory = get_app_factory()
        server_config = app_factory.get_server_config()
        
        logger.info(
            "Starting FastAPI server",
            host=server_config["host"],
            port=server_config["port"],
            debug=server_config["debug"],
            workers=server_config["workers"]
        )
        
        # Create the configured FastAPI app
        app = create_configured_app()
        
        # Run the server with Uvicorn
        uvicorn.run(
            app,
            host=server_config["host"],
            port=server_config["port"],
            reload=server_config["reload"],
            workers=server_config["workers"] if not server_config["reload"] else 1,
            log_level=server_config["log_level"],
            access_log=True
        )
        
    except Exception as e:
        logger.error("Failed to start FastAPI server", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
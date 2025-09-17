#!/usr/bin/env python3
"""
Command Line Interface for the AI Cold Calling Agent
"""
import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


async def start_agent(config_path: str = None):
    """Start the AI calling agent"""
    try:
        # Import here to allow CLI to work without dependencies
        from src.main import AICallingAgent
        
        agent = AICallingAgent(config_path)
        await agent.start()
        
        print("AI Cold Calling Agent is running. Press Ctrl+C to stop.")
        
        # Keep running
        while agent.is_running:
            await asyncio.sleep(1)
            
    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'agent' in locals():
            await agent.stop()


def validate_config(config_path: str):
    """Validate configuration file"""
    try:
        # Import here to allow CLI to work without dependencies
        from src.config import create_config_manager
        
        config_manager = create_config_manager(config_path)
        errors = config_manager.validate_config()
        
        if errors:
            print("Configuration validation failed:")
            for section, section_errors in errors.items():
                print(f"  {section}:")
                for error in section_errors:
                    print(f"    - {error}")
            sys.exit(1)
        else:
            print("Configuration is valid!")
            
    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error validating configuration: {e}")
        sys.exit(1)


def init_config():
    """Initialize configuration from example"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    example_config = config_dir / "config.example.yaml"
    main_config = config_dir / "config.yaml"
    
    if main_config.exists():
        print(f"Configuration file already exists: {main_config}")
        return
    
    if example_config.exists():
        # Copy example to main config
        with open(example_config, 'r') as src:
            content = src.read()
        
        with open(main_config, 'w') as dst:
            dst.write(content)
        
        print(f"Configuration initialized: {main_config}")
        print("Please edit the configuration file with your specific settings.")
    else:
        print("Example configuration not found!")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Cold Calling Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start                    # Start with default config
  %(prog)s start -c config.yaml    # Start with custom config
  %(prog)s validate                # Validate default config
  %(prog)s init                    # Initialize config from example
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the AI calling agent')
    start_parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file'
    )
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'start':
        asyncio.run(start_agent(args.config))
    elif args.command == 'validate':
        validate_config(args.config)
    elif args.command == 'init':
        init_config()


if __name__ == "__main__":
    main()
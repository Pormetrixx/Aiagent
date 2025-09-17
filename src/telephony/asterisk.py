"""
Asterisk integration module for the AI Cold Calling Agent
"""
import logging
import asyncio
import socket
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import threading
import queue

logger = logging.getLogger(__name__)


class AsteriskAMIManager:
    """Asterisk Manager Interface (AMI) integration for call management"""
    
    def __init__(self, host: str = "localhost", port: int = 5038, 
                 username: str = "admin", password: str = "secret"):
        """
        Initialize Asterisk AMI Manager
        
        Args:
            host: Asterisk server hostname/IP
            port: AMI port (default 5038)
            username: AMI username
            password: AMI password
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        self.socket = None
        self.connected = False
        self.authenticated = False
        self.action_id = 1
        
        # Event handling
        self.event_callbacks: Dict[str, List[Callable]] = {}
        self.response_queue = queue.Queue()
        self.event_thread = None
        self.running = False
        
        # Call tracking
        self.active_calls: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self) -> bool:
        """Connect to Asterisk AMI"""
        try:
            logger.info(f"Connecting to Asterisk AMI at {self.host}:{self.port}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # Read welcome message
            welcome = self.socket.recv(1024).decode('utf-8')
            logger.debug(f"AMI Welcome: {welcome.strip()}")
            
            self.connected = True
            
            # Start event listener thread
            self.running = True
            self.event_thread = threading.Thread(target=self._event_listener)
            self.event_thread.daemon = True
            self.event_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Asterisk AMI: {e}")
            return False
    
    async def login(self) -> bool:
        """Authenticate with Asterisk AMI"""
        if not self.connected:
            return False
        
        try:
            action = {
                "Action": "Login",
                "Username": self.username,
                "Secret": self.password,
                "ActionID": str(self.action_id)
            }
            
            response = await self._send_action(action)
            
            if response and response.get("Response") == "Success":
                self.authenticated = True
                logger.info("Successfully authenticated with Asterisk AMI")
                return True
            else:
                logger.error(f"AMI authentication failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error during AMI login: {e}")
            return False
    
    async def originate_call(self, phone_number: str, channel: str = "SIP", 
                           context: str = "outbound", extension: str = "s", 
                           priority: int = 1, caller_id: str = None) -> Dict[str, Any]:
        """
        Originate an outbound call through Asterisk
        
        Args:
            phone_number: Target phone number
            channel: Channel technology (SIP, PJSIP, etc.)
            context: Dialplan context
            extension: Extension to execute
            priority: Priority in dialplan
            caller_id: Caller ID to present
            
        Returns:
            Call result dictionary
        """
        if not self.authenticated:
            return {"success": False, "error": "Not authenticated"}
        
        try:
            # Generate unique call ID
            call_id = f"call_{int(time.time())}_{self.action_id}"
            
            # Prepare originate action
            action = {
                "Action": "Originate",
                "Channel": f"{channel}/{phone_number}",
                "Context": context,
                "Exten": extension,
                "Priority": str(priority),
                "ActionID": str(self.action_id),
                "Variable": f"CALL_ID={call_id}",
                "Async": "true"
            }
            
            if caller_id:
                action["CallerID"] = caller_id
            
            response = await self._send_action(action)
            
            if response and response.get("Response") == "Success":
                # Track the call
                self.active_calls[call_id] = {
                    "phone_number": phone_number,
                    "channel": f"{channel}/{phone_number}",
                    "start_time": datetime.utcnow(),
                    "status": "dialing",
                    "unique_id": None
                }
                
                logger.info(f"Successfully originated call to {phone_number}, call_id: {call_id}")
                return {
                    "success": True,
                    "call_id": call_id,
                    "message": "Call originated successfully"
                }
            else:
                error_msg = response.get("Message", "Unknown error") if response else "No response"
                logger.error(f"Failed to originate call to {phone_number}: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Error originating call to {phone_number}: {e}")
            return {"success": False, "error": str(e)}
    
    async def hangup_call(self, call_id: str) -> bool:
        """Hangup a call by call ID"""
        if call_id not in self.active_calls:
            logger.warning(f"Call {call_id} not found in active calls")
            return False
        
        call_info = self.active_calls[call_id]
        channel = call_info.get("channel")
        
        if not channel:
            return False
        
        try:
            action = {
                "Action": "Hangup",
                "Channel": channel,
                "ActionID": str(self.action_id)
            }
            
            response = await self._send_action(action)
            
            if response and response.get("Response") == "Success":
                # Update call status
                if call_id in self.active_calls:
                    self.active_calls[call_id]["status"] = "hung_up"
                    self.active_calls[call_id]["end_time"] = datetime.utcnow()
                
                logger.info(f"Successfully hung up call {call_id}")
                return True
            else:
                logger.error(f"Failed to hangup call {call_id}: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error hanging up call {call_id}: {e}")
            return False
    
    async def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific call"""
        return self.active_calls.get(call_id)
    
    async def list_active_calls(self) -> List[Dict[str, Any]]:
        """List all active calls"""
        try:
            action = {
                "Action": "Status",
                "ActionID": str(self.action_id)
            }
            
            response = await self._send_action(action)
            # Note: Status action returns multiple events, would need event handling
            
            return list(self.active_calls.values())
            
        except Exception as e:
            logger.error(f"Error listing active calls: {e}")
            return []
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """Register callback for specific AMI events"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    async def _send_action(self, action: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Send action to Asterisk AMI and wait for response"""
        if not self.connected:
            return None
        
        try:
            self.action_id += 1
            action["ActionID"] = str(self.action_id)
            
            # Format action as AMI protocol
            message = ""
            for key, value in action.items():
                message += f"{key}: {value}\r\n"
            message += "\r\n"
            
            # Send action
            self.socket.send(message.encode('utf-8'))
            
            # Wait for response (simple implementation - could be improved)
            await asyncio.sleep(0.1)
            
            # Try to get response from queue
            try:
                response = self.response_queue.get(timeout=5)
                if response.get("ActionID") == action["ActionID"]:
                    return response
            except queue.Empty:
                logger.warning(f"Timeout waiting for response to action {action['Action']}")
                return None
            
        except Exception as e:
            logger.error(f"Error sending AMI action: {e}")
            return None
    
    def _event_listener(self):
        """Background thread to listen for AMI events"""
        buffer = ""
        
        while self.running and self.connected:
            try:
                if self.socket:
                    data = self.socket.recv(4096).decode('utf-8')
                    if not data:
                        break
                    
                    buffer += data
                    
                    # Process complete messages
                    while "\r\n\r\n" in buffer:
                        message, buffer = buffer.split("\r\n\r\n", 1)
                        self._process_message(message)
                        
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Error in AMI event listener: {e}")
                break
        
        logger.info("AMI event listener stopped")
    
    def _process_message(self, message: str):
        """Process an AMI message (event or response)"""
        try:
            lines = message.strip().split("\r\n")
            data = {}
            
            for line in lines:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    data[key] = value
            
            if "Event" in data:
                self._handle_event(data)
            elif "Response" in data:
                self.response_queue.put(data)
                
        except Exception as e:
            logger.error(f"Error processing AMI message: {e}")
    
    def _handle_event(self, event_data: Dict[str, str]):
        """Handle AMI events"""
        event_type = event_data.get("Event", "")
        
        try:
            # Handle call-related events
            if event_type == "Newchannel":
                self._handle_new_channel(event_data)
            elif event_type == "Hangup":
                self._handle_hangup(event_data)
            elif event_type == "Dial":
                self._handle_dial_event(event_data)
            elif event_type == "Bridge":
                self._handle_bridge_event(event_data)
            
            # Trigger registered callbacks
            if event_type in self.event_callbacks:
                for callback in self.event_callbacks[event_type]:
                    try:
                        callback(event_data)
                    except Exception as e:
                        logger.error(f"Error in event callback: {e}")
                        
        except Exception as e:
            logger.error(f"Error handling event {event_type}: {e}")
    
    def _handle_new_channel(self, event_data: Dict[str, str]):
        """Handle new channel creation"""
        channel = event_data.get("Channel", "")
        unique_id = event_data.get("Uniqueid", "")
        
        # Try to match with our originated calls
        for call_id, call_info in self.active_calls.items():
            if call_info.get("channel") == channel:
                call_info["unique_id"] = unique_id
                call_info["status"] = "ringing"
                logger.debug(f"Channel created for call {call_id}: {channel}")
                break
    
    def _handle_hangup(self, event_data: Dict[str, str]):
        """Handle call hangup"""
        channel = event_data.get("Channel", "")
        cause = event_data.get("Cause", "")
        
        # Find and update call status
        for call_id, call_info in self.active_calls.items():
            if call_info.get("channel") == channel:
                call_info["status"] = "ended"
                call_info["end_time"] = datetime.utcnow()
                call_info["hangup_cause"] = cause
                logger.info(f"Call {call_id} ended, cause: {cause}")
                break
    
    def _handle_dial_event(self, event_data: Dict[str, str]):
        """Handle dial events"""
        channel = event_data.get("Channel", "")
        subevent = event_data.get("SubEvent", "")
        
        # Update call status based on dial events
        for call_id, call_info in self.active_calls.items():
            if call_info.get("channel") == channel:
                if subevent == "Begin":
                    call_info["status"] = "dialing"
                elif subevent == "Answer":
                    call_info["status"] = "answered"
                    call_info["answer_time"] = datetime.utcnow()
                logger.debug(f"Dial event for call {call_id}: {subevent}")
                break
    
    def _handle_bridge_event(self, event_data: Dict[str, str]):
        """Handle bridge events (when calls are connected)"""
        channel1 = event_data.get("Channel1", "")
        channel2 = event_data.get("Channel2", "")
        
        # Update call status for bridged calls
        for call_id, call_info in self.active_calls.items():
            if call_info.get("channel") in [channel1, channel2]:
                call_info["status"] = "connected"
                call_info["bridge_time"] = datetime.utcnow()
                logger.info(f"Call {call_id} bridged/connected")
                break
    
    async def disconnect(self):
        """Disconnect from Asterisk AMI"""
        self.running = False
        
        if self.authenticated:
            try:
                action = {
                    "Action": "Logoff",
                    "ActionID": str(self.action_id)
                }
                await self._send_action(action)
            except:
                pass
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.connected = False
        self.authenticated = False
        logger.info("Disconnected from Asterisk AMI")


class AsteriskTelephonyProvider:
    """High-level Asterisk telephony provider for the AI calling agent"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Asterisk telephony provider
        
        Args:
            config: Asterisk configuration dictionary
        """
        self.config = config
        self.ami = AsteriskAMIManager(
            host=config.get("host", "localhost"),
            port=config.get("port", 5038),
            username=config.get("username", "admin"),
            password=config.get("password", "secret")
        )
        
        # Call configuration
        self.channel_tech = config.get("channel_technology", "SIP")
        self.context = config.get("context", "outbound")
        self.extension = config.get("extension", "s")
        self.caller_id = config.get("caller_id", "AI Agent <1000>")
        
        # Event callbacks for the AI agent
        self.call_callbacks: Dict[str, Callable] = {}
    
    async def initialize(self) -> bool:
        """Initialize the telephony provider"""
        try:
            logger.info("Initializing Asterisk telephony provider")
            
            if not await self.ami.connect():
                return False
            
            if not await self.ami.login():
                return False
            
            # Register event handlers
            self.ami.register_event_callback("Dial", self._on_dial_event)
            self.ami.register_event_callback("Hangup", self._on_hangup_event)
            self.ami.register_event_callback("Bridge", self._on_bridge_event)
            
            logger.info("Asterisk telephony provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Asterisk provider: {e}")
            return False
    
    async def make_call(self, phone_number: str) -> Dict[str, Any]:
        """
        Make an outbound call
        
        Args:
            phone_number: Target phone number
            
        Returns:
            Call result with call_id if successful
        """
        try:
            # Clean phone number
            clean_number = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            
            logger.info(f"Making call to {clean_number} via Asterisk")
            
            result = await self.ami.originate_call(
                phone_number=clean_number,
                channel=self.channel_tech,
                context=self.context,
                extension=self.extension,
                caller_id=self.caller_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error making call to {phone_number}: {e}")
            return {"success": False, "error": str(e)}
    
    async def end_call(self, call_id: str) -> bool:
        """End an active call"""
        try:
            return await self.ami.hangup_call(call_id)
        except Exception as e:
            logger.error(f"Error ending call {call_id}: {e}")
            return False
    
    async def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a call"""
        return await self.ami.get_call_status(call_id)
    
    async def list_active_calls(self) -> List[Dict[str, Any]]:
        """List all active calls"""
        return await self.ami.list_active_calls()
    
    def register_call_callback(self, event_type: str, callback: Callable):
        """Register callback for call events"""
        self.call_callbacks[event_type] = callback
    
    def _on_dial_event(self, event_data: Dict[str, str]):
        """Handle dial events"""
        if "call_answered" in self.call_callbacks:
            subevent = event_data.get("SubEvent", "")
            if subevent == "Answer":
                self.call_callbacks["call_answered"](event_data)
    
    def _on_hangup_event(self, event_data: Dict[str, str]):
        """Handle hangup events"""
        if "call_ended" in self.call_callbacks:
            self.call_callbacks["call_ended"](event_data)
    
    def _on_bridge_event(self, event_data: Dict[str, str]):
        """Handle bridge events"""
        if "call_connected" in self.call_callbacks:
            self.call_callbacks["call_connected"](event_data)
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.ami.disconnect()
    
    def is_available(self) -> bool:
        """Check if Asterisk is available"""
        return self.ami.connected and self.ami.authenticated


def create_asterisk_provider(config: Dict[str, Any]) -> AsteriskTelephonyProvider:
    """Factory function to create Asterisk telephony provider"""
    return AsteriskTelephonyProvider(config)
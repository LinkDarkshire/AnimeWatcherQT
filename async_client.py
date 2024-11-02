import asyncio
import socket
from typing import Optional, Dict, Any
import urllib.parse
import json
import time

class AsyncAniDBClient:
    def __init__(self, credentials: dict, logger, max_retries: int = 3):
        if not isinstance(credentials, dict):
            raise ValueError("Credentials must be a dictionary")
        if 'username' not in credentials or 'password' not in credentials:
            raise ValueError("Credentials must contain 'username' and 'password'")
            
        self.credentials = credentials
        self.logger = logger
        self.session_key: Optional[str] = None
        self.socket = None
        self.server = 'api.anidb.net'
        self.port = 9000
        self.max_retries = max_retries
        self.timeout_count = 0
        self.last_command_time = 0
        self.logger.info("AsyncAniDBClient initialized")
        self.logger.debug(f"Initialized with username: {credentials['username']}")

    def _check_rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_command_time
        if time_since_last < 2:
            time.sleep(2 - time_since_last)
        self.last_command_time = time.time()

    def _handle_timeout(self):
        """Handle timeout and check if we should continue"""
        self.timeout_count += 1
        if self.timeout_count >= self.max_retries:
            self.logger.error(f"Maximum number of retries ({self.max_retries}) reached")
            raise Exception("Maximum number of timeouts reached")
        self.logger.warning(f"Timeout {self.timeout_count}/{self.max_retries}")
        time.sleep(2 * self.timeout_count)  # Exponential backoff

    async def send_command(self, command: bytes, expect_response: bool = True) -> Optional[str]:
        """Send command with retry logic"""
        self._check_rate_limit()
        
        for attempt in range(self.max_retries):
            try:
                self.socket.sendto(command, (self.server, self.port))
                
                if expect_response:
                    # Convert blocking socket operations to async
                    loop = asyncio.get_event_loop()
                    data, _ = await loop.run_in_executor(
                        None, 
                        lambda: self.socket.recvfrom(1024)
                    )
                    self.timeout_count = 0  # Reset on successful response
                    return data.decode('utf-8')
                return None
                
            except socket.timeout:
                self._handle_timeout()
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying command (attempt {attempt + 2}/{self.max_retries})")
                    await asyncio.sleep(2 * (attempt + 1))  # Use async sleep
                    continue
                raise

    async def __aenter__(self):
        self.logger.debug("Entering context manager")
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(10)  # 10 seconds timeout
            await self.authenticate()
            return self
        except Exception as e:
            self.logger.error(f"Error in context manager entry: {str(e)}")
            if self.socket:
                self.socket.close()
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Exiting context manager")
        try:
            if self.socket:
                await self.logout()
                self.socket.close()
                self.logger.info("Socket closed successfully")
        except Exception as e:
            self.logger.error(f"Error during context manager exit: {str(e)}")

    async def authenticate(self):
        self.logger.info("Starting authentication process")
        try:
            auth_command = (
                f"AUTH user={self.credentials['username']}&"
                f"pass={self.credentials['password']}&"
                "protover=3&"
                "client=lewdwatcher&"
                "clientver=1"
            ).encode('utf-8')

            # Log command (without password)
            safe_command = auth_command.decode('utf-8').replace(self.credentials['password'], '********')
            self.logger.debug(f"Sending auth command: {safe_command}")

            response = await self.send_command(auth_command)
            if not response:
                raise ValueError("No response from server")
            
            self.session_key = self._handle_auth_response(response)
            if not self.session_key:
                raise ValueError("Authentication failed")

            return True

        except socket.timeout:
            self.logger.error("Final authentication timeout")
            raise
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            raise

    async def query_anime(self, query: str, by_id: bool = False) -> Optional[Dict[str, Any]]:
        if not self.session_key:
            raise ValueError("Not authenticated")

        try:
            # Prepare command
            if by_id:
                command = f"ANIME aid={query}&"
            else:
                command = f"ANIME aname={urllib.parse.quote(query)}&"
            
            command += f"amask=b2f0e401070000&s={self.session_key}"
            
            self.logger.debug(f"Sending anime query: {command}")
            
            response = await self.send_command(command.encode('utf-8'))
            if not response:
                return None
                
            return self._process_anime_response(response)

        except socket.timeout:
            self.logger.error("Final query timeout")
            return None
        except Exception as e:
            self.logger.error(f"Query error: {str(e)}")
            return None

    async def logout(self):
        if self.session_key:
            try:
                command = f"LOGOUT s={self.session_key}"
                await self.send_command(command.encode('utf-8'), expect_response=False)
                self.logger.info("Logout command sent")
            except Exception as e:
                self.logger.warning(f"Error during logout: {str(e)}")

    def _handle_auth_response(self, response: str) -> Optional[str]:
        """Process authentication response"""
        self.logger.debug(f"Processing auth response: {response[:50]}...")

        try:
            parts = response.split()
            if len(parts) < 2:
                self.logger.error("Invalid auth response format")
                return None

            code = parts[0]
            if code in ['200', '201']:
                self.logger.info("Authentication successful")
                return parts[1]
            else:
                self.logger.error(f"Authentication failed with code: {code}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing auth response: {str(e)}")
            return None

    def _process_anime_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Process anime query response"""
        self.logger.debug("Processing anime response")

        try:
            lines = response.strip().split('\n')
            if len(lines) < 2:
                self.logger.error("Invalid response format")
                return None

            code = lines[0].split()[0]
            if code != '230':
                self.logger.error(f"Unexpected response code: {code}")
                return None

            parts = lines[1].split('|')
            result = {
                'aid': int(parts[0]),
                'year': parts[1],
                'type': parts[2],
                'romaji': parts[4],
                'kanji': parts[5],
                'english': parts[6],
                'synonyms': parts[7],
                'episodes': int(parts[8]) if parts[8].isdigit() else 0,
                'ep_count': int(parts[9]) if parts[9].isdigit() else 0,
                'special_count': int(parts[10]) if parts[10].isdigit() else 0,
                'tag_name_list': parts[11],
                'tag_id_list': parts[13],
                'tag_weigth_list': parts[14]
            }

            self.logger.debug(f"Successfully parsed anime data for ID: {result['aid']}")
            return result

        except Exception as e:
            self.logger.error(f"Error processing anime response: {str(e)}")
            return None

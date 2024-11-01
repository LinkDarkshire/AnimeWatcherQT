import asyncio
import aiohttp
from typing import Optional, Dict, Any
import json
import urllib.parse

class AsyncAniDBClient:
    def __init__(self, credentials: dict, logger):
        """
        Initialize the AsyncAniDBClient.
        
        Parameters
        ----------
        credentials : dict
            Dictionary containing 'username' and 'password'
        logger : Logger
            Logger instance
        """
        self.credentials = credentials
        self.logger = logger
        self.session: Optional[aiohttp.ClientSession] = None
        self.session_key: Optional[str] = None
        self.base_url = 'api.anidb.net'
        self.port = 9000
        self.logger.info("AsyncAniDBClient initialized")

    async def __aenter__(self):
        self.logger.debug("Entering context manager")
        if not self.credentials:
            self.logger.error("No credentials provided")
            raise       
        try:
            self.session = aiohttp.ClientSession(base_url=self.base_url)
            self.logger.debug("aiohttp session created")
            await self.authenticate()
            return self
        except Exception as e:
            self.logger.error(f"Error in context manager entry: {str(e)}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Exiting context manager")
        try:
            if self.session:
                await self.logout()
                await self.session.close()
                self.logger.info("Session closed successfully")
        except Exception as e:
            self.logger.error(f"Error during context manager exit: {str(e)}")

    async def authenticate(self):
        self.logger.info("Starting authentication process")
        if not self.credentials or 'username' not in self.credentials or 'password' not in self.credentials:
            self.logger.error("Invalid credentials")    
            raise
        try:
            credentials = self.config.get_anidb_credentials()
            if not credentials:
                self.logger.error("Authentication failed: No credentials found in config")
                raise ValueError("AniDB credentials not configured")

            # Erstelle den Auth-String
            auth_command = (
                f"AUTH user={self.credentials['username']}&"
                f"pass={self.credentials['password']}&"
                "protover=3&"
                "client=lewdwatcher&"
                "clientver=1"
            )

            # Erstelle den kompletten Befehl
            command = 'AUTH ' + '&'.join(f"{k}={v}" for k, v in auth_params.items())

            # Log request details (ohne Passwort)
            safe_params = auth_params.copy()
            safe_params['pass'] = '********'
            self.logger.debug(f"Auth command (masked): AUTH {safe_params}")

            # Sende den Befehl
            async with self.session.get('/' + command) as response:
                data = await response.text()
                self.logger.debug(f"Auth response status: {response.status}")
                self.session_key = self._handle_auth_response(data)

                if self.session_key:
                    self.logger.info("Authentication successful")
                    self.logger.debug(f"Session key obtained: {self.session_key[:5]}...")
                return self.session_key

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error during authentication: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication: {str(e)}")
            raise

    async def query_anime(self, query: str, by_id: bool = False) -> Optional[Dict[str, Any]]:
        self.logger.info(f"Querying anime {'by ID' if by_id else 'by name'}: {query}")

        if not self.session_key:
            self.logger.error("Query attempted without valid session")
            raise ValueError("Not authenticated")

        try:
            # Erstelle den ANIME-Befehl
            command_params = {
                'amask': 'b2f0e401070000',
                's': self.session_key
            }

            if by_id:
                command_params['aid'] = query
            else:
                command_params['aname'] = urllib.parse.quote(query)

            # Erstelle den kompletten Befehl
            command = 'ANIME ' + '&'.join(f"{k}={v}" for k, v in command_params.items())

            self.logger.debug(f"Query command: {command}")

            async with self.session.get('/' + command) as response:
                self.logger.debug(f"Query response status: {response.status}")

                if response.status != 200:
                    self.logger.warning(f"Unexpected response status: {response.status}")

                data = await response.text()
                self.logger.debug(f"Raw response data: {data[:200]}...")  # Log first 200 chars

                result = self._process_anime_response(data)

                if result:
                    self.logger.info(f"Successfully retrieved data for: {query}")
                    self.logger.debug(f"Processed response: {json.dumps(result, ensure_ascii=False)[:200]}...")
                else:
                    self.logger.warning(f"No data found for query: {query}")

                return result

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error during anime query: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error processing anime query: {str(e)}")
            raise

    async def logout(self):
        self.logger.info("Initiating logout")
        if self.session_key:
            try:
                command = f"LOGOUT s={self.session_key}"
                self.logger.debug("Sending logout request")

                async with self.session.get('/' + command) as response:
                    self.logger.debug(f"Logout response status: {response.status}")
                    if response.status == 200:
                        self.logger.info("Logout successful")
                    else:
                        self.logger.warning(f"Unexpected logout response: {response.status}")

            except Exception as e:
                self.logger.warning(f"Error during logout (non-critical): {str(e)}")
        else:
            self.logger.debug("Logout skipped - no active session")

    def _handle_auth_response(self, response_str: str) -> Optional[str]:
        """Handle authentication response and return session key if successful"""
        self.logger.debug(f"Processing auth response: {response_str[:50]}...")  # Log first 50 chars

        response_codes = {
            '200': "Login accepted",
            '201': "Login accepted (new version available)",
            '500': "Login Failed",
            '501': "Login Failed (No Login)",
            '502': "Access denied",
            '503': "Client outdated",
            '504': "Banned",
            '505': "Banned (too many failed logins)",
            '506': "Invalid Session"
        }

        try:
            code = response_str.split(' ')[0]

            if code in response_codes:
                self.logger.debug(f"Auth response code {code}: {response_codes[code]}")
            else:
                self.logger.warning(f"Unknown response code: {code}")

            if code in ['200', '201']:
                session_key = response_str.split(' ')[1]
                self.logger.info("Authentication successful")
                return session_key
            else:
                self.logger.error(f"Authentication failed: {response_codes.get(code, 'Unknown error')}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing auth response: {str(e)}")
            return None

    def _process_anime_response(self, data: str) -> Optional[Dict[str, Any]]:
        """Process anime query response data"""
        self.logger.debug("Processing anime response data")

        try:
            response_str = data.strip()
            code = response_str.split(' ')[0]

            if code != '230':
                self.logger.warning(f"Unexpected anime response code: {code}")
                return None

            parts = response_str.split('\n')[1].split('|')

            result = {
                'aid': int(parts[0]),
                'year': parts[1],
                'type': parts[2],
                'romaji': parts[4],
                'kanji': parts[5],
                'english': parts[6],
                'synonyms': parts[7],
                'episodes': int(parts[8]),
                'ep_count': int(parts[9]),
                'special_count': int(parts[10]),
                'tag_name_list': parts[11],
                'tag_id_list': parts[13],
                'tag_weigth_list': parts[14],
            }

            self.logger.debug(f"Successfully parsed anime data for ID: {result['aid']}")
            return result

        except IndexError as e:
            self.logger.error(f"Error parsing anime response - invalid format: {str(e)}")
            self.logger.debug(f"Raw response data: {data}")
            return None
        except ValueError as e:
            self.logger.error(f"Error parsing anime response - invalid values: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error processing anime response: {str(e)}")
            return None
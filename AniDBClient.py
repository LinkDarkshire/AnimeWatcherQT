import socket
import configparser
from AniDBFinderDialog import AniDBFinderDialog

class AniDBClient:
    """
    A class to interact with the AniDB API.

    Attributes
    ----------
    server : str
        The server address for the AniDB API.
    port : int
        The port number for the AniDB API.
    client : socket
        The socket object used for communication with the AniDB API.
    username : str
        The username for authentication.
    password : str
        The password for authentication.
    session_key : str
        The session key obtained after successful authentication.

    Methods
    -------
    __init__(prfdesc)
        Initializes the AniDBClient object by loading the user profiles,
        authenticating, and setting up the socket connection.

    load_profiles(prfdesc)
        Loads the username and password from the configuration file based on the provided profile description.

    authenticate()
        Authenticates the user with the AniDB API using the loaded username and password.

    query_anidb(anime_name)
        Queries the AniDB API for information about the specified anime.
        If the anime is not found, it prompts the user to select a hentai anime from a dialog box.

    process_response(response)
        Processes the response from the AniDB API and extracts the relevant anime information.

    close()
        Closes the socket connection and logs out from the AniDB API.
    """

    def __init__(self, prfdesc):
        self.server = 'api.anidb.net'
        self.port = 9000
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username, self.password = self.load_profiles(prfdesc)
        success, self.session_key = self.authenticate()
        if success == False:
            print(f"Error: closing programm Code: {self.session_key}")
            exit()

    def load_profiles(self, prfdesc):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if config.has_section(prfdesc):
            return config.get(prfdesc, 'username'), config.get(prfdesc, 'password')
        return None, None
    
    def authenticate(self):
        command = f'AUTH user={self.username}&pass={self.password}&protover=3&client=lewdwatcher&clientver=1'
        self.client.sendto(command.encode(), (self.server, self.port))
        response, _ = self.client.recvfrom(4096)
        response_str = response.decode('utf-8')
        if response_str.startswith('200') or response_str.startswith('201'):
            return True, response_str.split(' ')[1]
        if response_str.startswith('500'):
            print("Login Failed")
        if response_str.startswith('501'):
            print("Login Failed (No Login)")
        if response_str.startswith('502'):
            print("Access denied")
        if response_str.startswith('503'):
            print("Client outdated")
        if response_str.startswith('504'):
            print("Banned")  
        if response_str.startswith('506'):
            print("Invalid Session")                 
        return False, response_str.split(' ')[0]

    def query_anidb(self, anime_name):
        #amask = 'FFFFFFFFFF0000'
        amask = 'b2f0e401070000'
        command = f'ANIME aname={anime_name}&amask={amask}&s={self.session_key}'
        self.client.sendto(command.encode(), (self.server, self.port))
        response, _ = self.client.recvfrom(4096)
        response_str = response.decode('utf-8')

        if response_str.startswith('230'):
            return self.process_response(response)
        
        if response_str.startswith('330'):
            print(f"Hentai {anime_name} not found")
            hentaifinder = AniDBFinderDialog(anime_name) 
            if hentaifinder.exec_():
                id = hentaifinder.GetID()
                command = f'ANIME aid={id}&amask={amask}&s={self.session_key}'
                self.client.sendto(command.encode(), (self.server, self.port))
                response, _ = self.client.recvfrom(4096)
                response_str = response.decode('utf-8')
                return self.process_response(response)
            exit()
        
        if response_str.startswith('501'):
            print("Session closed ... relogging")
            self.close()
            success, self.session_key = self.authenticate()
            if success == False:
                print(f"Error: closing programm Code: {self.session_key}")
                exit()
            return self.query_anidb(anime_name)
        
        else:
            print(f"Error: closing programm Code: {self.session_key}")
            exit()

    def process_response(self, response):
        response_str = response.decode('utf-8')
        parts = response_str.split('\n')[1].split('|')
        anime_info = {
            'aid': int(parts[0]),
            'year': parts[1],
            'type': parts[2],
            'romaji': parts[4],
            'kanji': parts[5],
            'synonyms': parts[7],
            'episodes': int(parts[8]),
            'ep_count': int(parts[9]),
            'special_count': int(parts[10]),
            'tag_name_list': parts[11],
            'tag_id_list': parts[13],
            'tag_weigth_list': parts[14],
        }

        return anime_info

    def close(self):
        command = f'LOGOUT s={self.session_key}&tag=byebye'
        self.client.sendto(command.encode(), (self.server, self.port))
        response, _ = self.client.recvfrom(4096)
        response_str = response.decode('utf-8')
        if response_str.startswith('byebye'):
            self.client.close()
        else:
            print("Error during logout") 
            self.client.close()
            

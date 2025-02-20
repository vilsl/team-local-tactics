from core import Champion

from socket import socket, SOL_SOCKET, SO_REUSEADDR
import pickle
import csv

def _parse_champ(champ_text: str) -> Champion:
    """
    Parses input string and generates Champion. Returns Champion object.

    Parameters
    ----------
    champ_text : str
        String containing champion info 
    """
    name, rock, paper, scissors = champ_text.split(sep=',')
    return Champion(name, float(rock), float(paper), float(scissors))

def from_csv(filename: str) -> dict[str, Champion]:
    """
    Parses champions from some_champs.txt and returns a dict of Champions and their data.

    Parameters
    ----------
    filename : str
        Name of file to read champions from
    """
    champions = {}
    with open(filename, 'r') as f:
        for line in f.readlines():
            champ = _parse_champ(line)
            champions[champ.name] = champ
    return champions


def get_match_history():
    """
    Reads and returns match history from matches.txt. Returns an array of arrays of all matches.
    """
    matchHistory = []
    with open('matches.txt', 'r') as f:
        for line in f.readlines()[3:]: # Skip first three lines containing info and example match
            match = num, winner, p1Score, p2Score = line.split(sep=',')
            match[3] = match[3].strip()
            matchHistory.append(match)
    return matchHistory

def save_match(result):
    """
    Saves passed match result to matches.txt.
    Format: matchnum, playerwinner, player1score, player2score

    Parameters
    ----------
    result : tuple
        Player 1 and 2 from match
    """
    matchnum = 0
    # Get current match num
    with open ('matches.txt') as f:
        for line in f:
            pass
        last_line = line
        matchnum = int(last_line[0]) + 1 # Append to number of matches
    
    # Calculate and save match result (calc should maybe be done in server)
    with open('matches.txt', 'a') as f:
        # Find last line to get newest match num
        p1 = result[0]
        p2 = result[1]
        if p1 < p2: # P2 wins
            winner = "2"
        elif p2 < p1: # P1 wins
            winner = "1"
        else: # Draw
            winner = "0"
        f.write(f"\n{matchnum},{winner},{p1},{p2}") # Write result

def send_client(sock,conn,_,load): 
    """
    Pickle and send data back to connected client using TCP (usually server)

    Parameters
    ----------
    sock : socket
        Unused, actually.
    conn : socket
        Connection/socket that the request arrived through
    _ : tuple
        Address of who/whatever sent the request
    load : any
        Payload / data if any, champion stats or match history
    """

    pickled = pickle.dumps(load) #always pickle
    conn.send(pickled)
    print(f'Sent data to {_}, showing the unpickled format:\n{load}\n')

# Listen for commands and perform appropriate actions
def main():
    """
    Main loop. Sets up a listening socket for incoming requests.
    Read received data and performs the appropriate action, like
    saving data or returning data read from 'database' files. (.txt files)
    """
    with socket() as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(('localhost', 5556))
        sock.listen() # Should this be inside the loop?
        print('TNT Database online.')
        print(f'Listening at {sock.getsockname()}\n')

        while True: # Network loop
            print(f'Listening at {sock.getsockname()}\n')
            conn, _ = sock.accept()
            print(f'Peer {_} connected\n')
            with conn:
                # Get command and forward to server_command
                # Data will always be sent as an array consisting of command,data
                try:
                    received = pickle.loads(conn.recv(1024))
                except:
                    print(f"Lost connection to {_}\n") # Break loop and listen for new connections
                    break

                print(f'Received request from {_}:\n{received}\n')
                command = received[0]
                load = received[1]
                print(command)
                # Quit and shut down server if requested, else handle command
                if command == "GET_CHAMPS":
                    champions = from_csv('some_champs.txt')
                    send_client(sock,conn,_,champions)                
                    print("Sent champions")
                    conn.close()
                elif command == "SAVE_MATCH":
                    save_match(load)
                    send_client(sock,conn,_,"OK")
                elif command == "MATCH_HISTORY": # Returns a dict of all match history
                    send_client(sock,conn,_,get_match_history())
                elif command == "QUIT": #TODO quit command
                    conn.close()
                    sock.close()
                    break

if __name__ == '__main__':
    main()
import playermanager
import gamehistory_manager 
import sessionmanager

""" Do NOT create your own instances of SessionManager, PlayerManager and 
GameHistoryManager unless you are really sure you have to, but I cannot think 
of such a case. Use the ones supplied below and you will be fine. 
NEVER, UNDER NO CIRCUMSTANCES, create a new SessionManager instance, it will 
make SQLite fail and probably create other problems with other databases! 
I am serious! """

#: ONLY use this SessionManager. Creating multiple will make SQLite fail!
session_manager = sessionmanager.SessionManager()
#: ONLY use this PlayerManager as creating multiple is redundant.
player_manager = playermanager.PlayerManager(session_manager)
#: ONLY use this GameHistoryManager as creating multiple is redundant.
game_history_manager = gamehistory_manager.GameHistoryManager(session_manager)

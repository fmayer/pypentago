import actions

_avail_actions = ['registered', 'not_logged_in', 'display_player',
                  'turn_recv', 'in_game', 'email_available', 'name_available',
                  'login', 'game_over', 'gamelist', 'start', 'conn_lost', 
                  'conn_established']

gui = actions.Context(_avail_actions)
register_method = actions.register_method
register_handler = gui.register_handler
register_nostate_handler = gui.register_nostate_handler
remove_handler = gui.remove_handler
remove_function = gui.remove_function
delete_action = gui.delete_action
emmit_action = gui.emmit_action
register = gui.register
clear = gui.clear

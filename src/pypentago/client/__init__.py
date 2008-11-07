import actions

_avail_actions = ['registered', 'not_logged_in', 'display_player',
                  'turn_recv', 'in_game', 'email_available', 'name_available',
                  'login', 'game_over', 'gamelist', 'start', 'conn_lost', 
                  'conn_established']

context = actions.Context(_avail_actions)

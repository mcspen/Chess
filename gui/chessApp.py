from GUI import Application
import gameWindow


class ChessApp(Application):
    """
    The FifaApp class creates the application window and all of its functions.
    """

    def __init__(self):
        Application.__init__(self)

    def key_down(self, event):
        print 'Key down'
        if event.char == "E":
            raise Exception("This is a test exception.")

    def key_up(self, event):
        print 'Key up'

    def auto_key(self, event):
        print 'Auto key'


def start_app():
    app = ChessApp()
    gameWindow.open_game_window(300, 55)
    app.run()

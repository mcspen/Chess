import multiprocessing
import gui.chessApp


if __name__ == '__main__':
    multiprocessing.freeze_support()

    gui.chessApp.start_app()

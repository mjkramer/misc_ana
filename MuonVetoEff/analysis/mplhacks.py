import io
import matplotlib.pyplot as plt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication


def add_clipboard_to_figures():
    # use monkey-patching to replace the original plt.figure() function with
    # our own, which supports clipboard-copying
    oldfig = plt.figure

    def newfig(*args, **kwargs):
        fig = oldfig(*args, **kwargs)

        def add_figure_to_clipboard(event):
            if event.key == "ctrl+c":
                with io.BytesIO() as buffer:
                    fig.savefig(buffer)
                    image = QImage.fromData(buffer.getvalue())
                    QApplication.clipboard().setImage(image)

        fig.canvas.mpl_connect('key_press_event', add_figure_to_clipboard)
        return fig

    plt.figure = newfig


def mplhacks():
    add_clipboard_to_figures()

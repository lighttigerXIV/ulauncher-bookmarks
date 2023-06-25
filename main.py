from asyncio import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from enum import Enum

from pathlib import Path
import json
import webbrowser


class Function(Enum):
    ADD = 1
    REMOVE = 2
    OPEN = 3


class Terminal_Runner(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, RunCommand())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):

        icon_setting = extension.preferences["icon"]
        icon = f"images/icon-{icon_setting}.svg"

        query = event.get_argument().split()
        name = event.get_argument()
        bookmarks = get_bookmarks()
        results = []

        if len(name.strip()) == 0:
            return RenderResultListAction([])

        if "add" in query and "as" not in query:

            url = query[query.index("add") + 1] if len(query) > 1 else ""

            return RenderResultListAction([ExtensionResultItem(
                icon=icon,
                name=f"Name:",
                description=f"Url: {url}",
                on_enter=DoNothingAction())])

        if "add" in query and "as" in query:

            url = query[query.index("add") + 1]
            name_words = query[query.index("as") + 1: len(query)]
            name = ""

            for word in name_words:
                name = (f"{name}{word} ")

            name = name.strip()

            return RenderResultListAction([ExtensionResultItem(
                icon=icon,
                name=f"Name: {name}",
                description=f"Url: {url}",
                on_enter=ExtensionCustomAction({
                    "function": Function.ADD,
                    "name": name,
                    "url": url
                }))])

        if "remove" in query and len(query) == 1:

            return RenderResultListAction([])

        if "remove" in query:

            name_words = query[query.index("remove") + 1: len(query)]
            name = ""

            for word in name_words:
                name = (f"{name}{word} ")

            name = name.strip()

            for bookmark in bookmarks:
                if name in bookmark["name"].lower() or name in bookmark["url"].lower():
                    results.append(ExtensionResultItem(
                        icon=icon,
                        name=f"Remove {bookmark['name']}",
                        description=bookmark["url"],
                        on_enter=ExtensionCustomAction({
                            "function": Function.REMOVE,
                            "url": bookmark["url"]
                        })
                    ))

            return RenderResultListAction(results)

        if len(bookmarks) == 0 or name == "":
            results.append(ExtensionResultItem(
                icon=icon,
                name="Bookmark Not Found",
                description="You did a oopsie :P",
                on_enter=DoNothingAction()
            ))

        else:
            for bookmark in bookmarks:
                if name in bookmark["name"].lower() or name in bookmark["url"].lower():
                    results.append(ExtensionResultItem(
                        icon=icon,
                        name=bookmark['name'],
                        description=bookmark['url'],
                        on_enter=ExtensionCustomAction({
                            "function": Function.OPEN,
                            "url": bookmark["url"]
                        })
                    ))

        return RenderResultListAction(results)


def get_bookmarks_path():
    home_path = Path.home()
    return f"{home_path}/.config/ulauncher-bookmarks/bookmarks.json"


def init_settings():

    home_path = Path.home()
    folder = Path(f"{home_path}/.config/ulauncher-bookmarks/")

    if not folder.exists():
        folder.mkdir(parents=True)


def get_bookmarks():

    home_path = Path.home()
    bookmarks_path = Path(
        f"{home_path}/.config/ulauncher-bookmarks/bookmarks.json")

    if not bookmarks_path.exists():

        bookmarks_path.parent.mkdir(parents=True, exist_ok=True)
        file = open(bookmarks_path, "w")
        file.close()

        return []

    bookmarks_content = bookmarks_path.read_text()

    try:
        bookmarks = json.loads(bookmarks_content)
        return bookmarks
    except:
        return []


class RunCommand(EventListener):

    def on_event(self, event, extension):

        data = event.get_data()

        function = data["function"]

        init_settings()

        if function == Function.ADD:

            bookmarks = get_bookmarks()

            bookmarks.append({
                "name": data["name"],
                "url": data["url"]
            })

            with open(get_bookmarks_path(), "w") as file:
                file.write(json.dumps(bookmarks))

            return HideWindowAction()

        if function == Function.REMOVE:

            bookmarks = [bookmark for bookmark in get_bookmarks()
                         if bookmark["url"] != data["url"]]

            with open(get_bookmarks_path(), "w") as file:
                file.write(json.dumps(bookmarks))

            return HideWindowAction()

        if function == Function.OPEN:

            webbrowser.open(data["url"])

            return HideWindowAction()


if __name__ == '__main__':
    Terminal_Runner().run()

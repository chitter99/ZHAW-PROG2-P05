import asyncio
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Input
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem, InputState


class LocationAutocompleteInput(Widget):
    def __init__(
        self,
        placeholder,
        *children: Widget,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ) -> None:
        self.placeholder = placeholder

        # Used for efficient autocomplet
        self.location_task = None

        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def compose(self) -> ComposeResult:
        yield AutoComplete(
            Input(placeholder=self.placeholder),
            Dropdown(items=self.get_locations),
            id="search-container",
        )

    async def fetch_locations(self, input_state: InputState):
        await asyncio.sleep(0.4)

        completions = self.app.location_autocomplet_service.search_completion(
            input_state.value
        )

        matches = []
        for completion in completions:
            if "label" in completion:
                matches.append(DropdownItem(completion["label"]))

        dropdown = self.query_one(AutoComplete).dropdown
        dropdown.child.matches = matches
        dropdown.display = (
            len(matches) > 0
            and input_state.value != ""
            and dropdown.input_widget.has_focus
        )

    def get_locations(self, input_state: InputState) -> list[DropdownItem]:
        if self.location_task and not self.location_task.done():
            self.location_task.cancel()
        self.location_task = asyncio.create_task(self.fetch_locations(input_state))
        return []

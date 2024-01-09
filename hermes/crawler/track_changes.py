from dataclasses import dataclass


@dataclass
class PDFChanges:
    added: list[str]
    deleted: list[str]

    @property
    def is_changed(self):
        return bool(self.added or self.deleted)


def track_changes(new_paths: list[str], prev_paths: list[str]) -> PDFChanges:
    """Returns PDFChanges object with added and deleted PDFs."""
    return PDFChanges(
        added=list(set(prev_paths) - set(new_paths)),
        deleted=list(set(new_paths) - set(prev_paths)),
    )

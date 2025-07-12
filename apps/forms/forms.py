# core/forms.py

from django import forms
from django.utils.safestring import mark_safe

class TailwindFormMixin:
    base_class = (
        "mt-1 block w-full px-3 py-2 border border-gray-700 shadow-sm "
        "bg-gray-800 text-white focus:outline-none focus:ring-fox-orange focus:border-fox-orange"
        "focus:ring-2 focus:ring-fox-orange focus:border-fox-orange"
    )
    error_class = "border-red-500"
    label_class = "block text-sm font-medium text-gray-300"
    help_text_class = "mt-1 text-sm text-gray-400"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get("class", "")
            full_class = f"{existing_classes} {self.base_class}".strip()

            # Add red border if error present
            if self.errors.get(name):
                full_class += f" {self.error_class}"

            widget.attrs["class"] = full_class

            # Apply help text class via label + help injection
            field.label_suffix = ""
            field.help_text = mark_safe(
                f'<span class="{self.help_text_class}">{field.help_text}</span>'
            ) if field.help_text else ""

            # Wrap label manually for Tailwind styling
            field.label_tag = lambda *args, **kwargs: mark_safe(
                f'<label for="{widget.attrs.get("id", f"id_{name}")}" class="{self.label_class}">{field.label}</label>'
            )

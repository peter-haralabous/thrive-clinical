from crispy_tailwind.templatetags.tailwind_field import CrispyTailwindFieldNode
from crispy_tailwind.templatetags.tailwind_field import CSSContainer

# monkey-patch crispy-tailwind to use daisy styles
base_input = "input w-full"

default_styles = {
    "text": base_input,
    "number": base_input,
    "radioselect": "",
    "email": base_input,
    "url": base_input,
    "password": base_input,
    "hidden": "",
    "multiplehidden": "",
    "file": "",
    "clearablefile": "",
    "textarea": base_input,
    "date": base_input,
    "datetime": base_input,
    "time": base_input,
    "checkbox": "",
    "select": "",
    "nullbooleanselect": "",
    "selectmultiple": "",
    "checkboxselectmultiple": "",
    "multi": "",
    "splitdatetime": "text-gray-700 bg-white focus:outline border border-gray-300 leading-normal px-4 appearance-none"
    " rounded-lg py-2 focus:outline-none mr-2",
    "splithiddendatetime": "",
    "selectdate": "",
    "error_border": "input-error",
}

CrispyTailwindFieldNode.default_container = CSSContainer(default_styles)

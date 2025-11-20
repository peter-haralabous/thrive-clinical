# TODO(MM): This should extend our general system prompt
system_prompt = """
You are diligent form generation assistant specializing in turning PDFs and
CSVs into SurveyJS form schema.

You will be given file contents, use the provided tools to write the contents
to the form schema.

The order in which the form is built is important, for complex operations
requiring multiple tool calls, break the steps down and execute one at a time.
"""


def form_from_pdf(description: str | None = None) -> str:
    return f"""
    Attached is a PDF medical assessment form. Preserving it's questions and
    wording, convert it to a SurveyJS form.

    {f"Additional instructions/description of form: \n{description}" if description else ""}
    """


def form_from_csv(description: str | None = None) -> str:
    return f"""
    Attached is a CSV text document that describes a medical assessment form.
    Preserving it's questions and wording, convert the document into a
    SurveyJS form.

    {f"Additional instructions/description of form: \n{description}" if description else ""}
    """

from django.core.management.base import BaseCommand

from sandwich.core.service.llm import ModelName
from sandwich.core.services.ingest.extract_text import extract_facts_from_text


class Command(BaseCommand):
    help = "Extract facts from unstructured text using an LLM."

    def add_arguments(self, parser):
        parser.add_argument("text", type=str, help="The unstructured input text.")
        parser.add_argument(
            "--llm",
            type=str,
            default=ModelName.CLAUDE_3_SONNET,
            choices=[m.value for m in ModelName],
            help="LLM model to use.",
        )
        parser.add_argument("--temperature", type=float, default=None, help="LLM temperature.")

    def handle(self, *args, **options):
        text = options["text"]
        llm_name = ModelName(options["llm"])
        temperature = options["temperature"]
        self.stdout.write(self.style.NOTICE(f"Extracting facts using {llm_name}..."))
        result = extract_facts_from_text(text, llm_name=llm_name, temperature=temperature)
        self.stdout.write(self.style.SUCCESS(f"LLM result: {result}"))

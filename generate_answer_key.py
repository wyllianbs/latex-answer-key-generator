import re
import sys
from typing import List, Dict, Optional
from pathlib import Path


class Answer:
    """Representa uma resposta de questão."""

    def __init__(self, question_number: int, answer: str) -> None:
        self.question_number = question_number
        self.answer = answer

    def __repr__(self) -> str:
        return f"Answer(q{self.question_number}, {self.answer})"


class LatexParser:
    """Parser para extrair respostas de arquivos LaTeX."""

    def __init__(self, content: str) -> None:
        self.content = content
        self.answers: List[Answer] = []

    def parse(self) -> List[Answer]:
        """Extrai todas as respostas do conteúdo LaTeX."""
        items = re.split(r'\\item\s+\\rtask', self.content)

        for question_number, item in enumerate(items[1:], start=1):
            answer = self._extract_answer_from_item(item, question_number)
            if answer:
                self.answers.append(answer)

        return self.answers

    def _extract_answer_from_item(self, item: str, question_number: int) -> Optional[Answer]:
        """Extrai a resposta de um item individual."""
        answerlist_match = re.search(
            r'\\begin\{answerlist\}.*?\\end\{answerlist\}',
            item,
            re.DOTALL
        )

        if answerlist_match:
            answerlist_content = answerlist_match.group(0)

            answer_text = self._extract_true_false_answer(answerlist_content)

            if not answer_text:
                answer_text = self._extract_multiple_choice_answer(answerlist_content)

            if answer_text:
                return Answer(question_number, answer_text)

        answer_text = self._extract_comment_answer(item)
        if answer_text:
            return Answer(question_number, answer_text)

        print(f"Aviso: Não foi possível encontrar resposta para a questão {question_number}.")
        return None

    def _extract_true_false_answer(self, answerlist_content: str) -> Optional[str]:
        """Extrai resposta de questões Verdadeiro/Falso."""
        doneitem_match = re.search(r'\\doneitem\[([VF])[.\]]', answerlist_content)
        if doneitem_match:
            return doneitem_match.group(1)
        return None

    def _extract_multiple_choice_answer(self, answerlist_content: str) -> Optional[str]:
        """Extrai resposta de questões de múltipla escolha."""
        lines = re.findall(r'\\(ti|di)(?:\s|\[)', answerlist_content)

        if lines:
            try:
                di_position = lines.index('di')
                return chr(65 + di_position)
            except ValueError:
                pass

        return None

    def _extract_comment_answer(self, item: str) -> Optional[str]:
        """Extrai resposta de comentários (método alternativo)."""
        comment_match = re.search(r'%\s*([VF])\s*$', item, re.MULTILINE)
        if comment_match:
            return comment_match.group(1)
        return None


class CSVExporter:
    """Exportador de respostas para formato CSV com múltiplas colunas."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def export(self, all_answers: Dict[str, List[Answer]], file_names: List[str]) -> None:
        """Exporta as respostas de múltiplos arquivos para um único CSV."""
        try:
            max_questions = max(len(answers) for answers in all_answers.values())

            with open(self.output_path, 'w', encoding='utf-8') as f:
                for i in range(max_questions):
                    question_label = f"q{i + 1}"
                    row_values = [question_label]

                    for file_name in file_names:
                        answers = all_answers[file_name]
                        if i < len(answers):
                            row_values.append(answers[i].answer)
                        else:
                            row_values.append("")

                    f.write(",".join(row_values) + "\n")

            print(f"\nGabarito salvo com sucesso em: {self.output_path}")
            print(f"Total de questões processadas: {max_questions}")
            print(f"Total de versões: {len(file_names)}")

        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            sys.exit(1)


class AnswerKeyGenerator:
    """Gerador principal de gabarito para múltiplos arquivos."""

    def __init__(self, input_files: List[str], output_file: str) -> None:
        self.input_paths = [Path(f) for f in input_files]
        self.output_path = Path(output_file)

    def run(self) -> None:
        """Executa o processo completo de geração do gabarito."""
        all_answers: Dict[str, List[Answer]] = {}
        file_names: List[str] = []

        for input_path in self.input_paths:
            print(f"\nProcessando {input_path}...")
            latex_content = self._read_latex_file(input_path)

            parser = LatexParser(latex_content)
            answers = parser.parse()

            if not answers:
                print(f"Aviso: Nenhuma resposta encontrada em {input_path}.")
                continue

            file_name = input_path.stem
            all_answers[file_name] = answers
            file_names.append(file_name)

            print(f"  → {len(answers)} questões encontradas em {input_path.name}")

        if not all_answers:
            print("Nenhuma resposta foi encontrada em nenhum arquivo.")
            sys.exit(1)

        exporter = CSVExporter(self.output_path)
        exporter.export(all_answers, file_names)

        self._show_preview(all_answers, file_names)

    def _read_latex_file(self, input_path: Path) -> str:
        """Lê o conteúdo do arquivo LaTeX."""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo '{input_path}' não encontrado.")
            sys.exit(1)
        except Exception as e:
            print(f"Erro ao ler arquivo '{input_path}': {e}")
            sys.exit(1)

    def _show_preview(self, all_answers: Dict[str, List[Answer]], file_names: List[str]) -> None:
        """Exibe um preview das respostas em formato tabular."""
        max_questions = max(len(answers) for answers in all_answers.values())
        preview_count = min(10, max_questions)

        header = f"  {'questao':<10}" + "".join(f"{name:<10}" for name in file_names)
        print(f"\nPreview das primeiras {preview_count} respostas:")
        print(header)
        print("  " + "-" * (10 + 10 * len(file_names)))

        for i in range(preview_count):
            row = f"  {'q' + str(i + 1):<10}"
            for file_name in file_names:
                answers = all_answers[file_name]
                if i < len(answers):
                    row += f"{answers[i].answer:<10}"
                else:
                    row += f"{'':<10}"
            print(row)

        if max_questions > 10:
            print(f"  ... e mais {max_questions - 10} questões")


def derive_default_output(input_files_str: str) -> str:
    """Deriva o nome padrão do arquivo de saída."""
    files = input_files_str.split()
    if not files:
        return "gabarito.csv"

    first_stem = Path(files[0]).stem

    if len(files) > 1:
        stems = [Path(f).stem for f in files]
        common = stems[0]
        for stem in stems[1:]:
            while not stem.startswith(common) and common:
                common = common[:-1]
            if not common:
                break

        if common:
            return f"{common}.csv"
        else:
            return f"{first_stem}.csv"
    else:
        return f"{first_stem}.csv"


def get_user_input(prompt: str, default: str) -> str:
    """Solicita entrada do usuário com valor padrão."""
    user_input = input(f"{prompt} (padrão: {default}): ").strip()
    return user_input if user_input else default


def main() -> None:
    """Função principal."""
    default_input = "P1A.tex P1B.tex P1C.tex"

    input_files_str = get_user_input(
        "Digite o(s) caminho(s) do(s) arquivo(s) LaTeX",
        default_input
    )

    input_files = input_files_str.split()

    default_output = derive_default_output(input_files_str)

    output_file = get_user_input(
        "Digite o nome do arquivo CSV de saída",
        default_output
    )

    generator = AnswerKeyGenerator(input_files, output_file)
    generator.run()


if __name__ == "__main__":
    main()

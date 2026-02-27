# 📝 Gerador de Gabarito LaTeX Para CSV

Código para extração de gabaritos de provas escritas em LaTeX e exportá-los em formato CSV para ser usado como _input_ em sistema OMR (_Optical Mark Recognition_), _e.g._, https://github.com/Udayraj123/OMRChecker/. Desenvolvido com **Orientação a Objetos** e **Type Hints** completos.

## 🎯 Funcionalidades

- ✅ **Extração automática** de respostas de arquivos LaTeX.
- ✅ **Suporte a múltiplos arquivos** (múltiplas versões de prova em uma única execução).
- ✅ **Suporte a múltiplos formatos** de questões:
  - Múltipla escolha (A, B, C, D, E)
  - Verdadeiro/Falso (V/F)
- ✅ **Exportação em CSV** com uma coluna por versão de prova, para fácil integração com sistemas de correção.
- ✅ **Interface interativa** com valores padrão.
- ✅ **Derivação automática** do nome do arquivo de saída com base nos arquivos de entrada.
- ✅ **Arquitetura OOP** com separação de responsabilidades.
- ✅ **Type Hints** completos para melhor manutenção.
- ✅ **Preview tabular** das respostas extraídas por versão.

## 📋 Pré-requisitos

- Python 3.7 ou superior.
- Nenhuma dependência externa necessária (usa apenas biblioteca padrão).

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/latex-answer-key-generator.git

# Acesse o diretório
cd latex-answer-key-generator

# Execute o código
python3 generate_answer_key.py
```

## 📖 Como Usar

### Uso Básico

```bash
python3 generate_answer_key.py
```

O programa solicitará:
1. **Arquivo(s) LaTeX de entrada** separados por espaço (padrão: `P1A.tex P1B.tex P1C.tex`).
2. **Arquivo CSV de saída** (padrão derivado automaticamente dos nomes dos arquivos de entrada).

Pressione `Enter` para usar os valores padrão ou digite caminhos personalizados. Os arquivos `.tex` podem ser gerados conforme código disponível em https://github.com/wyllianbs/carderno_prova.

### Exemplo de Execução

```bash
$ python3 generate_answer_key.py
Digite o(s) caminho(s) do(s) arquivo(s) LaTeX (padrão: P1A.tex P1B.tex P1C.tex):
Digite o nome do arquivo CSV de saída (padrão: P1.csv):

Processando P1A.tex...
  → 10 questões encontradas em P1A.tex

Processando P1B.tex...
  → 10 questões encontradas em P1B.tex

Processando P1C.tex...
  → 10 questões encontradas em P1C.tex

Gabarito salvo com sucesso em: P1.csv
Total de questões processadas: 10
Total de versões: 3

Preview das primeiras 10 respostas:
  questao   P1A       P1B       P1C
  ----------------------------------------
  q1        V         F         C
  q2        C         A         V
  q3        C         B         F
  ...
```

## 📄 Formato do Arquivo LaTeX

### Questões de Múltipla Escolha

O código identifica questões de múltipla escolha através dos comandos `\ti` e `\di`:

```latex
\item \rtask \ponto{\pt} Qual é a capital do Estado do Paraná?

\begin{answerlist}[label={\texttt{\Alph*}.},leftmargin=*]
  \ti São Paulo.
  \ti Rio de Janeiro.
  \di Curitiba.  % Resposta correta (posição C)
  \ti Florianópolis.
  \ti Belo Horizonte.
\end{answerlist}
```

**Resultado:** `q1,C`

### Questões Verdadeiro/Falso

O código identifica questões V/F através do comando `\doneitem`:

```latex
\item \rtask \ponto{\pt} Python é uma linguagem de programação.

% V
{\setlength{\columnsep}{0pt}\renewcommand{\columnseprule}{0pt}
\begin{multicols}{2}
  \begin{answerlist}[label={\texttt{\Alph*}.},leftmargin=*]
    \ifnum\gabarito=1\doneitem[V.]\else\ti[V.]\fi % Resposta correta (V)
    \ti[F.]
  \end{answerlist}
\end{multicols}
}
```

**Resultado:** `q1,V`

## 🏗️ Arquitetura

O projeto segue princípios de **Clean Code** e **SOLID**:

```
generate_answer_key.py
├── Answer                  # Modelo de dados para resposta
├── LatexParser             # Parser de arquivos LaTeX
├── CSVExporter             # Exportador para formato CSV multi-versão
├── AnswerKeyGenerator      # Orquestrador principal (múltiplos arquivos)
├── derive_default_output() # Derivação automática do nome de saída
└── main()                  # Ponto de entrada
```

### Classes Principais

#### `Answer`
Representa uma resposta individual com número da questão e alternativa.

```python
answer = Answer(question_number=1, answer="C")
print(answer)  # Answer(q1, C)
```

#### `LatexParser`
Responsável por extrair respostas do conteúdo LaTeX.

```python
parser = LatexParser(latex_content)
answers = parser.parse()
```

#### `CSVExporter`
Gerencia a exportação das respostas de múltiplas versões de prova para um único CSV. Recebe um dicionário mapeando o nome de cada versão para sua lista de respostas.

```python
exporter = CSVExporter(Path("gabarito.csv"))
exporter.export(all_answers, file_names)
```

#### `AnswerKeyGenerator`
Coordena o processo de geração do gabarito para múltiplos arquivos LaTeX simultaneamente.

```python
generator = AnswerKeyGenerator(["P1A.tex", "P1B.tex", "P1C.tex"], "P1.csv")
generator.run()
```

#### `derive_default_output()`
Função auxiliar que deriva automaticamente o nome do arquivo CSV de saída com base no prefixo comum entre os arquivos de entrada.

```python
derive_default_output("P1A.tex P1B.tex P1C.tex")  # retorna "P1.csv"
derive_default_output("prova.tex")                  # retorna "prova.csv"
```

## 📊 Formato de Saída

O arquivo CSV gerado consolida todas as versões de prova em colunas, seguindo o formato:

```csv
q1,V,F,C
q2,C,A,V
q3,F,B,F
q4,E,C,A
q5,A,D,B
q6,B,E,D
```

em que:
- **Primeira coluna**: Identificador da questão (`q1`, `q2`, ...).
- **Demais colunas**: Resposta de cada versão de prova (`A`–`E` para múltipla escolha, `V`/`F` para verdadeiro/falso), na ordem em que os arquivos foram fornecidos.

O arquivo de saída CSV pode ser usado como _input_ em um sistema OMR (_Optical Mark Recognition_), _e.g._, https://github.com/Udayraj123/OMRChecker/.

## 🎨 Exemplo Completo

Veja os arquivos [`P1A.tex`](P1A.tex), [`P1B.tex`](P1B.tex) e [`P1C.tex`](P1C.tex) (https://github.com/wyllianbs/carderno_prova) incluídos no repositório para exemplos completos de provas LaTeX compatíveis com o gerador.

### Estrutura do P1A.tex

```latex
\begin{enumerate}[resume=*questions,label={\arabic*.},leftmargin=*]
  \setcounter{rtaskno}{0}
  
  % Questão 1 - Verdadeiro/Falso
  \item \rtask \ponto{\pt} Lorem ipsum...
  % V
  {\setlength{\columnsep}{0pt}
  \begin{multicols}{2}
    \begin{answerlist}[label={\texttt{\Alph*}.},leftmargin=*]
      \ifnum\gabarito=1\doneitem[V.]\else\ti[V.]\fi
      \ti[F.]
    \end{answerlist}
  \end{multicols}
  }
  
  % Questão 2 - Múltipla Escolha
  \item \rtask \ponto{\pt} Lorem ipsum...
  \begin{answerlist}[label={\texttt{\Alph*}.},leftmargin=*]
    \ti Opção A
    \ti Opção B
    \di Opção C  % Resposta correta
    \ti Opção D
    \ti Opção E
  \end{answerlist}
  
\end{enumerate}
```

## 🔧 Personalização

### Modificando Padrões

Edite a função `main()` para alterar os arquivos padrão:

```python
def main() -> None:
    default_input = "ProvaA.tex ProvaB.tex"  # Novos padrões

    input_files_str = get_user_input(
        "Digite o(s) caminho(s) do(s) arquivo(s) LaTeX",
        default_input
    )
    ...
```

### Adicionando Novos Formatos

Para suportar novos tipos de questões, estenda a classe `LatexParser`:

```python
class LatexParser:
    def _extract_custom_answer(self, content: str) -> Optional[str]:
        # Implemente sua lógica aqui
        pass
```

## 🐛 Tratamento de Erros

O programa valida:
- ✅ Existência de cada arquivo LaTeX especificado.
- ✅ Formato correto dos arquivos LaTeX.
- ✅ Presença de questões em pelo menos um documento.
- ✅ Permissões de escrita no diretório de saída.
- ✅ Codificação UTF-8 dos arquivos.

### Mensagens de Erro Comuns

```bash
# Arquivo não encontrado
Erro: Arquivo 'prova.tex' não encontrado.

# Nenhuma resposta detectada em um arquivo (aviso, não encerra)
Aviso: Nenhuma resposta encontrada em P1B.tex.

# Nenhuma resposta em nenhum arquivo (encerra)
Nenhuma resposta foi encontrada em nenhum arquivo.

# Resposta não detectada em questão específica
Aviso: Não foi possível encontrar resposta para a questão 5.
```

## 🧪 Testando

### Teste Manual

```bash
# Use os arquivos de exemplo incluídos
python3 generate_answer_key.py
# Pressione Enter duas vezes para usar P1A.tex P1B.tex P1C.tex
```

### Validação do CSV

```bash
# Visualize o gabarito gerado
cat P1.csv

# Conte o número de questões
wc -l P1.csv
```

## 📚 Requisitos Técnicos

### Type Hints

O código utiliza type hints completos para melhor IDE support:

```python
def parse(self) -> List[Answer]:
    ...

def export(self, all_answers: Dict[str, List[Answer]], file_names: List[str]) -> None:
    ...
```

### Orientação a Objetos

Princípios aplicados:
- **Single Responsibility Principle**: Cada classe tem uma responsabilidade única.
- **Open/Closed Principle**: Fácil extensão sem modificação.
- **Dependency Inversion**: Dependência de abstrações, não implementações.

## 📜 Licença

Este projeto está licenciado sob a Licença [GNU General Public License v3.0](LICENSE).

## 👤 Autor

**Prof. Wyllian B. da Silva**  
Universidade Federal de Santa Catarina (UFSC)  
Departamento de Informática e Estatística (INE)

---

**Nota**: Este projeto foi desenvolvido especificamente para uso na UFSC, mas pode ser facilmente adaptado para outras instituições de ensino.

# Aplicação manual no GitHub

## Opção 1, pelo navegador

1. Abra o repositório `EduMiranda78/Analisador`.
2. Abra `README.md`.
3. Clique no ícone de lápis.
4. Substitua todo o conteúdo pelo arquivo `README.md` deste pacote.
5. Clique em `Commit changes`.
6. Volte à página principal.
7. Clique em `Add file` e depois em `Create new file`.
8. Crie `.env.example` usando o conteúdo do arquivo correspondente.
9. Repita o processo para `.gitignore`.
10. Edite a área `About` usando os dados de `ABOUT_REPOSITORY.txt`.

## Opção 2, pelo terminal

Copie estes arquivos para a pasta local do projeto e execute:

```bash
git add README.md .env.example .gitignore
git commit -m "docs: documenta instalação e configuração do projeto"
git push origin main
```

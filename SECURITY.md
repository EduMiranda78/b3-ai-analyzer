# Política de Segurança

## Versões suportadas

O projeto está em desenvolvimento.

Somente o código disponível na branch `main` recebe correções de segurança.

## Como relatar uma vulnerabilidade

Não publique vulnerabilidades, chaves de API, tokens, senhas ou outros dados sensíveis em Issues públicas.

Para enviar um relato privado:

1. Acesse a aba **Security and quality** do repositório.
2. Entre em **Advisories**.
3. Clique em **Report a vulnerability**.
4. Descreva o problema, o impacto e os passos necessários para reprodução.

Inclua, quando possível:

- versão ou commit afetado;
- arquivo ou componente envolvido;
- passos para reproduzir;
- impacto identificado;
- sugestão de correção;
- evidências sem dados pessoais ou credenciais.

O relato será analisado antes de qualquer divulgação pública.

## Segredos expostos

Se uma chave, token ou senha for publicada acidentalmente:

1. revogue imediatamente a credencial;
2. gere uma nova credencial;
3. remova o segredo do histórico do Git;
4. revise os logs de utilização;
5. verifique se houve acesso não autorizado.

Nunca envie arquivos `.env` para o repositório.

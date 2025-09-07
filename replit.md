# Overview

Este é um Sistema de Gerenciamento de Filmes baseado em Flask, projetado para organizar filmes armazenados em discos rígidos externos conectados a uma configuração de TV. A aplicação fornece uma interface web moderna para catalogar, navegar e gerenciar uma coleção pessoal de filmes. Os usuários podem adicionar filmes manualmente ou escanear drives externos para detecção automática, visualizar detalhes de filmes com posters, acompanhar status de "assistido", e organizar por gênero, ano e classificação.

# Preferências do Usuário

Estilo de comunicação preferido: Linguagem simples e cotidiana.

# Arquitetura do Sistema

## Arquitetura Frontend
O frontend usa um design responsivo moderno construído com Bootstrap 5 e gradientes CSS personalizados para uma interface elegante adequada para TV. A arquitetura inclui:
- **Template Engine**: Templates Jinja2 com padrão de herança de template base
- **Estilização**: Framework Bootstrap 5 com gradientes CSS personalizados e animações
- **JavaScript**: JavaScript vanilla para interações dinâmicas incluindo escaneamento de drives, auto-save de formulários e atualizações em tempo real
- **Design Responsivo**: Abordagem mobile-first adequada tanto para telas de TV quanto dispositivos móveis

## Arquitetura Backend
O backend segue um padrão MVC simples do Flask com separação clara de responsabilidades:
- **Framework Web**: Flask com roteamento e templating integrados
- **Manipulação de Arquivos**: Utilitários Werkzeug para uploads seguros de arquivos e gerenciamento de posters
- **Processamento de Imagem**: PIL (Python Imaging Library) para otimização de imagens de poster
- **Detecção de Drive Externo**: Capacidades nativas de escaneamento de drives em nível de SO
- **Integração de API**: Suporte para APIs de bancos de dados de filmes externos para busca de metadados

## Armazenamento de Dados
A aplicação usa SQLite como solução principal de banco de dados:
- **Banco de Dados**: SQLite com uma única tabela `movies` contendo metadados abrangentes de filmes
- **Schema**: Inclui campos para título, ano, gênero, diretor, descrição, caminhos de arquivo, caminhos de poster, classificação, duração, timestamps e status de assistido
- **Armazenamento de Arquivos**: Armazenamento local no sistema de arquivos para posters de filmes no diretório `static/uploads`
- **Persistência de Dados**: Todas as informações de filmes e preferências do usuário armazenadas localmente

## Segurança e Gerenciamento de Arquivos
- **Segurança de Upload**: Manipulação segura de nomes de arquivo usando utilitários Werkzeug
- **Limites de Tamanho de Arquivo**: Tamanho máximo de arquivo de 16MB para uploads de poster
- **Validação de Entrada**: Validação de formulário tanto no lado cliente quanto servidor
- **Tratamento de Erros**: Logging abrangente e gerenciamento de erros

# Dependências Externas

## Dependências Principais
- **Flask**: Framework web para aplicações Python
- **SQLite3**: Interface de banco de dados Python integrada
- **Werkzeug**: Biblioteca utilitária WSGI para manipulação segura de arquivos
- **PIL (Pillow)**: Python Imaging Library para processamento de imagens
- **Requests**: Biblioteca HTTP para chamadas de API externas

## Dependências Frontend
- **Bootstrap 5.1.3**: Framework CSS via CDN
- **Font Awesome 6.0.0**: Biblioteca de ícones via CDN
- **CSS Personalizado**: Temas de gradiente e animações

## Dependências do Sistema
- **Acesso a Drive Externo**: Acesso ao sistema de arquivos em nível de SO para escaneamento de drives conectados
- **Operações do Sistema de Arquivos**: Módulos nativos Python os e filesystem

## Integrações Opcionais
- **APIs de Banco de Dados de Filmes**: Suporte para buscar metadados de filmes de serviços externos
- **APIs de Imagem**: Capacidade de baixar posters de filmes de fontes externas

# Alterações Recentes

## 07 de Setembro de 2025
- Criado sistema completo de gerenciamento de filmes em Flask
- Implementada interface moderna com gradientes CSS e design responsivo
- Adicionada funcionalidade de detecção automática de drives externos
- Desenvolvidas páginas para listar, adicionar, editar e visualizar detalhes de filmes
- Implementado sistema de banco de dados SQLite para persistência
- Configurado workflow para execução do servidor Flask na porta 5000
- Interface otimizada para uso em TV com navegação intuitiva

# Estrutura do Projeto

```
/
├── app.py                 # Aplicação Flask principal
├── movies.db             # Banco de dados SQLite (criado automaticamente)
├── templates/            # Templates HTML
│   ├── base.html         # Template base com navegação
│   ├── index.html        # Página inicial com dashboard
│   ├── movies.html       # Lista de filmes
│   ├── add_movie.html    # Formulário para adicionar filme
│   ├── edit_movie.html   # Formulário para editar filme
│   └── movie_detail.html # Página de detalhes do filme
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados com gradientes
│   ├── js/
│   │   └── app.js        # JavaScript para funcionalidades dinâmicas
│   └── uploads/          # Diretório para posters de filmes
└── replit.md            # Este arquivo de documentação
```

O sistema está pronto para uso e pode detectar drives externos, escanear arquivos de filme e gerenciar uma coleção completa de filmes com interface moderna adequada para uso em TV.
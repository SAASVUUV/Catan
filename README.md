# Catan
Como começar (ambiente Windows):

1. Ativa o ambiente virtual:

    .\\venv\\Scripts\\Activate.ps1

2. Instale dependências:

   python -m pip install pygame

3. Execute o jogo:

   python main.py

Para executar a suíte por grupos de casos com o driver:

    python drivers.py --list
    python drivers.py --group domain
    python drivers.py --group all -- --cov=. --cov-report=term-missing
